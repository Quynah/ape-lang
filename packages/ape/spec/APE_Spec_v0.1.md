# Ape Language Specification — v0.1 (Draft)

Author: David Van Aelst  
Status: Prototype / Draft  
Version: 0.1.0

---

## 1. Filosofie

Ape is een AI-native taal met één centrale gedachte:

> What is allowed, is fully allowed.  
> What is forbidden, is strictly forbidden.  
> What is not declared, does not exist.

Doelen:

- deterministisch gedrag als standaard
- ambiguïteit is illegaal (compile-time errors)
- gecontroleerde creativiteit via **Controlled Deviation System (CDS)**
- syntaxis die voor AI én mens goed leesbaar is

Ape is bedoeld als een “Because I Said So”-taal: alles wat mag, wordt expliciet toegestaan; alles wat niet beschreven wordt, bestaat niet voor de taal.

---

## 2. Overzicht taalconstructies

Top-level constructs:

- `entity` — gestructureerde data
- `enum` — beperkte set waarden
- `task` — bewerkende logica met expliciete inputs/outputs
- `flow` — orchestratie van stappen en tasks
- `policy` — declaratieve regels over gedrag
- `allow deviation` — controlled deviation blok als onderdeel van `constraints`

Een Ape-bestand (`.ape`) bestaat uit één of meerdere top-level definities.

---

## 3. Basis syntaxis

### 3.1 Indentation

- Ape is indentation-based (zoals Python/YAML).
- Indent-niveau definieert blokstructuur (body van entities, tasks, flows, policies).
- Tabs zijn verboden; spaties met vaste breedte (bij voorkeur 4 spaties) worden gebruikt.
- Tokenizer herkent expliciet INDENT/DEDENT; inconsistent indentation leidt tot parse-fouten.

### 3.2 Entities

> Gestructureerde records met benoemde velden.

Conceptuele vorm:

```ape
entity CalculationRequest:
    left: decimal
    right: decimal
    op: Operation
```

Eigenschappen:

- Velden bestaan uit `naam: type`.
- Types kunnen primitief of user-defined zijn (andere entities/enums).
- De SemanticValidator controleert:
  - dubbel gedefinieerde velden
  - types die niet bestaan

### 3.3 Enums

> Gesloten set van symbolische waarden.

Voorbeeld:

```ape
enum ThreatLevel:
    - LOW
    - MEDIUM
    - HIGH
```

Kenmerken:

- waarden worden gedefinieerd als lijst met `- VALUE`.
- enums worden als types gebruikt in entities en tasks.

### 3.4 Tasks

> Functie-achtige constructies met expliciete inputs en outputs.

Conceptuele vorm:

```ape
task calculate:
    inputs:
        request: CalculationRequest
    outputs:
        result: CalculationResult

    constraints:
        - deterministic

    steps:
        - beschrijf de berekening in natural language
```

Eigenschappen:

- `inputs:` — lijst van naam + type.
- `outputs:` — lijst van naam + type (v0.1: meestal één output).
- `constraints:` — lijst van string-constraints en optioneel één of meer `allow deviation`-blokken.
- `steps:` — natural language instructies.  
  De StrictnessEngine controleert hier o.a. op ambiguïteit (bijv. vage formuleringen, impliciete keuzes).

### 3.5 Flows

> Orchestratie van tasks en stappen.

Voorbeeld:

```ape
flow calculator_demo:
    constraints:
        - deterministic

    steps:
        - create CalculationRequest with left = 1, right = 2, op = "add"
        - run task calculate
        - print result.result to the console
```

Eigenschappen:

- `constraints:` — zelfde mechanisme als bij tasks.
- `steps:` — beschrijven opeenvolgende acties in natural language:
  - aanmaken van entities
  - aanroepen van tasks
  - loggen/printen, etc.
- Semantiek wordt door tooling/AI geïnterpreteerd; Ape zelf valideert structuur en strictness.

### 3.6 Policies

> Declaratieve regels over gewenst gedrag.

Eenvoudig voorbeeld (structuur afhankelijk van implementatie):

```ape
policy email_threat_policy:
    rules:
        - emails from trusted domains are always LOW
        - emails with HIGH assessment must be quarantined
```

Eigenschappen:

- `policy` heeft een naam en één of meer regels (meestal tekstueel).
- SemanticValidator controleert basisstructuur (bijv. dat een policy tenminste een regel bevat).
- Policies kunnen later door runtime-systemen of tooling geïnterpreteerd worden.

---

## 4. Typesysteem

### 4.1 Primitieve types

Standaard primitieve types in v0.1:

- `string`
- `integer`
- `decimal`
- `boolean`
- `datetime`
- `date`

De Python-codegenerator mapt deze types naar passende Python-types (bv. `str`, `int`, `float`, `bool`, `datetime.datetime`, `datetime.date`).

### 4.2 Samengestelde / afgeleide types

- `list T` — lijst van elementen van type `T`
- user-defined types:
  - `entity`-namen
  - `enum`-namen

Type-resolutie:

- Types moeten bekend zijn op het moment van gebruik (of in hetzelfde module-bereik gedefinieerd zijn).
- Onbekende types leiden tot semantische fouten:
  - bij entities: onbekende veldtypes
  - bij tasks: onbekende input/output types

---

## 5. Constraints en Controlled Deviation System (CDS)

### 5.1 Gewone constraints

Een `constraints:`-blok kan eenvoudige string-constraints bevatten, bijvoorbeeld:

```ape
constraints:
    - deterministic
    - idempotent per day
```

Kenmerken:

- Strings worden semantisch geïnterpreteerd door `SemanticValidator` en tooling.
- Specifieke constraints kunnen later effect hebben op codegeneratie of runtime-gedrag.

Voorbeelden van conventionele constraints:

- `deterministic`
- `idempotent`
- `no side effects`
- domeinspecifieke regels (bv. “no external calls”)

### 5.2 Controlled Deviation: `allow deviation`

Controlled Deviation definieert **expliciet** waar en hoe ambiguïteit / creativiteit is toegestaan.

Algemene vorm:

```ape
constraints:
    - deterministic
    - allow deviation:
        scope: steps
        mode: creative
        bounds:
            - result.result must equal the mathematically correct outcome
            - summary must describe the operation and outcome
            - no additional side effects are allowed
        rationale: "Formatting can vary"
```

#### Velden

- `scope`  
  Geeft aan **waar** de afwijking geldt, bijvoorbeeld:
  - `steps`
  - `task`
  - `flow`
  - `strategy` (optioneel / toekomst)
- `mode`  
  Type afwijking, v0.1 ondersteunt een beperkte set (bijv.):
  - `creative`
  - `semantic_choice`
  - `fuzzy_goal`
- `bounds`  
  Lijst van regels waarbinnen de vrijheid moet blijven:
  - beschrijven harde beperkingen op gedrag/resultaat
  - minstens één regel is verplicht
- `rationale`  
  Optionele uitleg voor de developer/AI waarom deze deviation bestaat en hoe hij bedoeld is.

#### Gedrag in de compiler

- De parser vertaalt `allow deviation`-blokken naar `DeviationNode`-instanties in AST en IR.
- De `SemanticValidator` controleert:
  - dat `scope` een geldige waarde heeft
  - dat `mode` een geldige waarde heeft
  - dat `bounds` niet leeg is
- De `StrictnessEngine`:
  - staat ambiguïteit toe binnen de gemarkeerde scope **mits** er een geldige `DeviationNode` is
  - blijft ambiguïteit buiten alle deviation-blokken als fout behandelen

---

## 6. Compiler pipeline

De volledige Ape toolchain bestaat uit de volgende stappen:

1. **Tokenization**  
   - Source → tokens
   - Herkent:
     - keywords (`entity`, `enum`, `task`, `flow`, `policy`, …)
     - identifiers
     - string-literals
     - INDENT/DEDENT
   - Ongeldige tekens of onverwachte indents geven lexicale fouten.

2. **Parsing**  
   - Tokens → AST
   - Bouwt AST-nodes voor:
     - module
     - entities, enums, tasks, flows, policies
     - constraints en deviation-blokken (`DeviationAST`)
   - Syntaxisfouten leiden tot parse-errors.

3. **IR building**  
   - AST → IR
   - Genereert IR-nodes zoals:
     - `ModuleNode`
     - `EntityNode`
     - `EnumNode`
     - `TaskNode`
     - `FlowNode`
     - `PolicyNode`
     - `DeviationNode`
   - Structuur is gericht op verdere analyse en codegeneratie.

4. **Semantic validation**  
   - IR → semantische fouten (of leeg)
   - Voorbeelden van checks:
     - dubbele definities van entities/tasks/enums/policies
     - onbekende types in entities en tasks
     - leegte of inconsistentie in definities (bijv. enum zonder waarden)
     - validiteit van deviation-blokken (scope/mode/bounds)

5. **Strictness enforcement**  
   - IR → strictness-fouten
   - Voorbeelden:
     - ambigue `steps` zonder passende deviation
     - impliciete keuzes zonder declaratie
     - gebruik van randomness in een strikt deterministische context
   - De StrictnessEngine houdt rekening met `DeviationNode` om toegestane afwijkingen te onderscheiden van illegale ambiguïteit.

6. **Code generation**  
   - IR → target-specifieke code (Python in v0.1)
   - Python-codegenerator:
     - entities → dataclasses
     - enums → Python classes/constanten
     - tasks → Python-functies met type hints
     - flows → orchestratiefuncties + metadata
     - policies → Python-structuren
     - deviaties → informatie in docstrings/metadata

7. **Runtime**  
   - Gegenereerde code gebruikt `aperuntime` (v0.1: `RunContext`) voor context:
     - bijv. tenant-id, metadata, toekomstige logging/tracing
   - Runtime is minimalistisch in v0.1, maar biedt een haak om later uitgebreid gedrag aan op te hangen.

---

## 7. CLI

Ape wordt geleverd met een command-line interface om `.ape`-bestanden te inspecteren, valideren en te builden.

Voorbeeld-commando's:

```bash
# AST inspecteren
python -m ape parse examples/calculator_basic.ape

# IR inspecteren
python -m ape ir examples/calculator_basic.ape

# Validatie (semantic + strictness)
python -m ape validate examples/calculator_basic.ape

# Code genereren (Python)
python -m ape build examples/calculator_basic.ape --target=python --out-dir=generated
```

Eigenschappen:

- `parse`  
  - Bouwt de AST en toont een eenvoudige representatie (debugging / inspectie).
- `ir`  
  - Bouwt IR en serialiseert deze naar een JSON-achtige weergave (debugging / tooling).
- `validate`  
  - Draait SemanticValidator + StrictnessEngine.
  - Exitcode:
    - `0` bij geen fouten
    - `1` bij één of meer fouten
- `build`  
  - Valideert eerst.
  - Genereert dan Python-code (voor target `python`).
  - Schrijft gegenereerde bestanden weg onder de opgegeven output directory.
  - Exitcode:
    - `0` bij succesvolle build
    - `1` bij validatie- of build-errors

---

## 8. Voorbeelden

### 8.1 `calculator_basic.ape`

Doel:

- Laat de basis constructs zien:
  - `enum Operation`
  - `entity CalculationRequest`
  - `entity CalculationResult`
  - `task calculate`
  - `flow calculator_demo`
- Geen deviation; volledig deterministisch.

Eigenschappen:

- eenvoudige vier-bewerkingen rekenmachine
- constraints: `deterministic`
- steps zijn eenduidig en zonder ambiguïteit

### 8.2 `calculator_smart.ape`

Doel:

- Zelfde domein als `calculator_basic`, maar met Controlled Deviation.

Eigenschappen:

- berekening van het resultaat blijft strikt deterministisch:
  - `result.result` moet exact de wiskundig correcte uitkomst zijn
- een `allow deviation`-blok geeft vrijheid in de `summary`-tekst:
  - scope: `steps`
  - mode: `creative`
  - bounds definiëren dat de summary:
    - de juiste getallen en uitkomst moet bevatten
    - geen extra side effects mag introduceren

Resultaat:  
Ape laat deterministische kern + gecontroleerde creativiteit in één task zien.

### 8.3 `email_policy_basic.ape`

Doel:

- Demonstreert hoe enums, entities, tasks en policies samen een eenvoudig e-maildreigingsmodel vormen.

Typische structuur:

- `enum ThreatLevel` (LOW/MEDIUM/HIGH)
- `entity Email` (bijv. `from_domain`, `subject`, `body`)
- `entity EmailAssessment` (bijv. `email`, `level`, `reason`)
- `task assess_email`:
  - inputs: `email: Email`
  - outputs: `assessment: EmailAssessment`
  - constraints: `deterministic`
  - steps: regels om threat-level te bepalen
- `policy email_threat_policy`:
  - regels m.b.t. hoe om te gaan met LOW/MEDIUM/HIGH e-mails

Gebruik:

- test-case voor semantische validatie
- voorbeeld hoe policies en tasks elkaar inhoudelijk versterken

---

## 9. Toekomstige uitbreidingen (indicatief)

Deze sectie beschrijft ideeën waarvoor v0.1 al de basis legt, maar die nog niet volledig zijn uitgewerkt.

Mogelijke richtingen:

- Rijkere policy-syntaxis (bijv. gestructureerde scope, stages)
- Expliciete triggers voor flows (bijv. `trigger:`-blokken voor tijd/gebeurtenissen)
- Extra codegen-backends (naast Python)
- Uitgebreidere runtime-hooks:
  - logging
  - tracing
  - metrics
- Formele grammar (bijv. EBNF) van de taal

---

## 10. Open Design Topics (for v0.2+)

Deze sectie beschrijft ideeën die bewust **nog niet** in v0.1 zitten, maar wel al richting geven voor toekomstige versies.

### 10.1 Deviation scoping & propagatie

**v0.1 gedrag (vastgezet)**

- Een `allow deviation`-blok geldt alleen voor het construct waarin het gedeclareerd is.
- Er is geen automatische “bubbeling” of overerving:
  - deviation in een `task` geldt niet automatisch voor de `flow` die die task aanroept.
- StrictnessEngine kijkt naar DeviationNodes per task/flow, lokaal.

**Mogelijke richting voor v0.2**

- Expliciete propagatie van deviation, bijvoorbeeld:

  ```ape
  constraints:
      - deterministic
      - allow deviation:
          scope: steps
          mode: creative
          bounds:
              - ...
          propagate: flow
  ```

- Optionele veldwaarde `propagate:` met mogelijke waarden zoals:
  - `none` (default, v0.1 gedrag)
  - `flow`
  - `children` (voor toekomstige nesting)

**Ontwerpregels**

- Geen impliciete overerving: propagatie moet expliciet zijn.
- StrictnessEngine moet altijd kunnen bepalen:
  - *waar* een deviation geldt
  - *wie* die deviation “leent”.
- Backwards compatibility: v0.1-code zonder `propagate` moet identiek blijven werken.

---

### 10.2 Policy-stages: compile, deploy, runtime

**v0.1 gedrag (vastgezet)**

- `policy` is declaratief, zonder expliciet onderscheid in “wanneer” ze geldt.
- De SemanticValidator controleert basissemantiek (bijv. bestaan van types/structuren).
- Policies worden niet hard gekoppeld aan compile-/runtime in de compiler zelf.

**Mogelijke richting voor v0.2**

- Een extra veld `stage:` op policies:

  ```ape
  policy ape_strict_deviation_policy:
      stage: compile
      rules:
          - all tasks must declare deterministic
          - all deviation blocks must define at least 2 bounds
  ```

  ```ape
  policy email_threat_policy:
      stage: runtime
      rules:
          - emails from trusted domains are always LOW
          - emails with HIGH assessment must be quarantined
  ```

- Voorbeelden:

  - **compile-time policies**  
    afdwingen tijdens `validate`/`build` (bijv. strengheidsregels voor deviation).
  - **deployment-time policies**  
    gebruikt bij rollout / configuratie per omgeving.
  - **runtime policies**  
    geïnterpreteerd door runtime/omliggende systemen tijdens uitvoering.

**Ontwerpregels**

- Compile-time policies mogen build blokkeren; andere stages niet.
- Policies moeten machine-leesbaar zijn, niet alleen tekst.
- Stages moeten optioneel zijn; v0.1-policies zonder `stage` blijven geldig.

---

### 10.3 Error taxonomy

**v0.1 gedrag (vastgezet)**

- Er zijn verschillende soorten fouten:
  - syntaxis-/parse errors (tokenizer/parser)
  - semantische fouten (SemanticValidator)
  - strictness-fouten (StrictnessEngine)
  - deviation-validatiefouten (CDS)
- Implementatie: errorcodes en boodschappen bestaan, maar nog niet als formele hiërarchie.

**Mogelijke richting voor v0.2**

Introduceer een expliciete foutclassificatie:

- Hoge-level categorieën:

  - `DeterminismError`
  - `AmbiguityError`
  - `DeviationError`
  - `PolicyError`
  - `ScopeViolation`
  - `TypeError`
  - `SyntaxError`

- Machine-leesbare codes, bijvoorbeeld:

  - `APE_DET_001` – determinisme geschonden
  - `APE_DEV_001` – unbounded deviation (lege bounds)
  - `APE_AMB_001` – impliciete keuze zonder deviation
  - `APE_POL_001` – policy-conflict

- Mens-leesbare boodschappen:

  - voldoende context: constructnaam, locatie, korte uitleg.

**Ontwerpregels**

- Elke error: (categorie, code, message).
- CLI/LSP/IDE kunnen op categorie & code sturen.
- Consistente mapping: dezelfde fout → dezelfde code, ongeacht tool.

---

### 10.4 Uitbreiding CDS-modes

**v0.1 gedrag (vastgezet)**

- Ondersteunde `mode`-waarden voor `allow deviation` zijn bewust beperkt
  (bijv. `creative`, `semantic_choice`, `fuzzy_goal`).
- Elke mode moet:
  - formeel begrensd zijn via `bounds`
  - door StrictnessEngine te controleren zijn

**Mogelijke extra modes (conceptueel)**

- `heuristic`  
  AI mag heuristieken gebruiken zolang uitkomst binnen bepaalde kwaliteits-bounds blijft.

- `probabilistic`  
  Gedrag mag probabilistisch zijn, met expliciete bounds op uitkomstruimte / waarschijnlijkheden.

- `exploratory`  
  Meerdere strategieën mogen verkennen, maar binnen duidelijke resource- en resultaat-bounds.

- `bounded_nondeterministic`  
  Meerdere mogelijke uitkomsten toegestaan, zolang alle uitkomsten binnen een gedefinieerde set/bounds vallen.

**Ontwerpregels**

- Nieuwe modes worden alleen toegevoegd als:
  - er een duidelijke definitie is van *toegestane vrijheid*
  - StrictnessEngine kan verifiëren dat gedrag binnen bounds blijft
- Modes mogen nooit het kernprincipe breken:
  - geen “ongecontroleerde” non-determinism
  - geen impliciete vrijheid zonder expliciete bounds
