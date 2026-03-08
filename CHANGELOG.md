# Changelog

## v0.1.2 (2026-03-08)

[Compare changes](https://github.com/thememium/dspy-guardrails/compare/v0.1.1...v0.1.2)

### 💅 Refactors

- **guardrail**: replace class factories with functions and use Sequence typing ([82270de](https://github.com/thememium/dspy-guardrails/commit/82270de34f92fd175bd2c8d6f95b09e8fa2c3d29))

### 📖 Documentation

- **quickstart**: streamline guide, add usage patterns, and clarify installation ([745437f](https://github.com/thememium/dspy-guardrails/commit/745437f9013616ac66200158c0f34eabc4ce4faa))
- **readme**: add early return example ([2865249](https://github.com/thememium/dspy-guardrails/commit/286524910bce5bb882d0d8adc699e840a3741b6a))
- **readme**: add documentation links to guardrail types table ([1cdb4e8](https://github.com/thememium/dspy-guardrails/commit/1cdb4e8849d551ad7386326cc8b811cb8fa3f427))
- **guardrail-types**: rewrite and expand guardrail types documentation ([9b3ca08](https://github.com/thememium/dspy-guardrails/commit/9b3ca08eac7144de006287ee454d2de7fca5a98a))
- **readme**: add “Available Guardrails” section with usage table ([9e2484c](https://github.com/thememium/dspy-guardrails/commit/9e2484c79ca29eef4ff00820d5c5b39b5191b23a))
- **readme**: trim outdated setup and example sections ([efb587a](https://github.com/thememium/dspy-guardrails/commit/efb587a81bb4a964b65a5ebfb724e8f029c488de))
- **readme**: add uv installation guide and pip alternative ([32995af](https://github.com/thememium/dspy-guardrails/commit/32995afba707140023f607d664016c1803fe1545))
- **readme**: restructure usage section and remove outdated advanced configuration ([2fc6462](https://github.com/thememium/dspy-guardrails/commit/2fc6462260575d6af4dfe8dab26d2125f3fd4df9))
- **contributing**: add comprehensive contributing guide for DSPy Guardrails ([875143a](https://github.com/thememium/dspy-guardrails/commit/875143ad116d3949d4ccbbb50785f03fd2d26a6f))
- **issue**: add GitHub bug‑report issue template ([dacab5a](https://github.com/thememium/dspy-guardrails/commit/dacab5a815a4b925e7949695ad5cfc741049717f))
- add SECURITY.md with vulnerability reporting guidelines and security notes ([0914ce9](https://github.com/thememium/dspy-guardrails/commit/0914ce9f3e8f7c837df9a0659188738be1b55721))
- add MIT License file ([eb8e88e](https://github.com/thememium/dspy-guardrails/commit/eb8e88e94129c2f05d4e5a3c2f81a6ce0c393819))
- **readme**: restructure README, add table of contents, usage and contribution sections ([29e53d2](https://github.com/thememium/dspy-guardrails/commit/29e53d29707ae2bb3b754c5a37cd20bbf1d5b041))
- **readme**: simplify README and remove Marimo‑specific references ([8490279](https://github.com/thememium/dspy-guardrails/commit/84902799ff6daac9ebb819509081a2d3529b7c29))
- add Guardrail Types reference documentation ([6bbb861](https://github.com/thememium/dspy-guardrails/commit/6bbb8610d580ceaf8721b7390b96b27e3fb4de19))
- remove obsolete MIGRATION_GUIDE.md ([2894788](https://github.com/thememium/dspy-guardrails/commit/28947889cfd8b3f4063ab3249049092ef10aece4))
- **AGENTS**: remove outdated AGENTS.md file ([d487bdd](https://github.com/thememium/dspy-guardrails/commit/d487bddc17a3cdef6d4c74df4ff270ebbf202d20))

### 🏡 Chore

- **pyproject**: update deptry script and extend its configuration ([16fe93d](https://github.com/thememium/dspy-guardrails/commit/16fe93dcd469a4820523c4ae9664a15323d1359f))
- **openspec**: delete obsolete OpenSpec docs and archived change files ([89c5a5b](https://github.com/thememium/dspy-guardrails/commit/89c5a5b0235083498e6ef0a64197eef376d93a4a))
- remove deprecated OpenSpec and RalphSpec command docs ([23893cd](https://github.com/thememium/dspy-guardrails/commit/23893cd1513c3a1d7e8b85ccde40872803504b3d))
- **notebooks**: delete obsolete guardrail notebook files ([6ce750c](https://github.com/thememium/dspy-guardrails/commit/6ce750c1e3e1fc185bc5984c6a65125dea63efbf))
- **pyproject**: trim dependencies to only dspy and add example task ([6e1d27d](https://github.com/thememium/dspy-guardrails/commit/6e1d27d86abb9476eac33154cd63552e4bdae8de))

### ✅ Tests

- split guardrail tests into separate files and add shared fixture ([0294325](https://github.com/thememium/dspy-guardrails/commit/02943255e6f47f9f1f4a554df40d4784fbdfe333))
- **tests**: add smoke test for dspy‑guardrails import and public API ([d5d54ed](https://github.com/thememium/dspy-guardrails/commit/d5d54ed587b1c28dfb9b961da563f22ce9a66b69))
- **guardrail**: add thorough unit tests for guardrail type classes ([37f2d47](https://github.com/thememium/dspy-guardrails/commit/37f2d47ce0a5159008fd9fa67774c35d35dfd016))

### Contributors

- Edward Boswell <thememium@gmail.com>

## v0.1.1 (2026-03-08)

### 🚀 Enhancements

- **example.py**: update Gemini language model version ([671a1b8](https://github.com/thememium/dspy-guardrails/commit/671a1b8ffdf12a164d601c3f2e4f583a675df8e2))
- **guardrail**: expose new guardrail factories and extend Run API ([f794231](https://github.com/thememium/dspy-guardrails/commit/f79423173a1cb9b49363d14f51412ff04967c4ec))
- **guardrails**: expose new guardrail classes ([e7743e9](https://github.com/thememium/dspy-guardrails/commit/e7743e9700a4191b24bb0786369ae00219235d50))
- **guardrails**: add toxicity detection guardrail ([5f59854](https://github.com/thememium/dspy-guardrails/commit/5f59854e75e47098fd2a0e8152c405d1ea0f3ee6))
- **guardrails**: add tone guardrail implementation ([8076152](https://github.com/thememium/dspy-guardrails/commit/80761526aee1cb0b824f58627e855bc7f9fd1d3f))
- **guardrails**: add language detection guardrail ([dbfed7e](https://github.com/thememium/dspy-guardrails/commit/dbfed7ec053cdcd18c87699c5f87fcb8cbad12e3))
- **guardrails**: add grounding guardrail implementation ([b25efba](https://github.com/thememium/dspy-guardrails/commit/b25efbae4fc2c3fade17c3a8c4e7a5b7eac88b8a))
- **gibberish**: add gibberish detection guardrail ([d5211ab](https://github.com/thememium/dspy-guardrails/commit/d5211ab59260b3d98b8433529f6248192f9328d8))
- **guardrails**: make NSFW list configurable; add allowed PII filter ([b5737a9](https://github.com/thememium/dspy-guardrails/commit/b5737a9df3fa13f5ad67c3e7707e360964a7b59e))
- **guardrails**: support kwargs in check methods and safe keyword handling ([e7c81ef](https://github.com/thememium/dspy-guardrails/commit/e7c81ef6fd9adc82e1bef9d904875be77e579e9b))
- **core**: add **kwargs support to guardrail checks and extend configurations ([ff0a825](https://github.com/thememium/dspy-guardrails/commit/ff0a825ff0d5872070dbfb390d1437192baa2811))
- **pyproject**: add CLI script entry and specify uv_build backend ([9724d40](https://github.com/thememium/dspy-guardrails/commit/9724d40a8d1109ab2fc838e39cdd3a618924899c))
- **guardrail**: add class‑based guardrail constructors and deprecate functions ([c78b306](https://github.com/thememium/dspy-guardrails/commit/c78b306a248ca28beb8adaec5338c6637feaced2))
- **dspy_guardrails**: expose additional guardrail classes and Run in __init__ ([77185a2](https://github.com/thememium/dspy-guardrails/commit/77185a2a1eeb001014eafe1253a15034d0653bbf))
- **guardrails/keywords**: add simple string‑matching fallback when DSPy is unavailable ([0eb2c66](https://github.com/thememium/dspy-guardrails/commit/0eb2c66034c1f8f383d584f7c18834b7744e3051))
- **example.py**: enhance console output for guardrail Run results ([981ad15](https://github.com/thememium/dspy-guardrails/commit/981ad154a7458e3ef7a1b78a69e13d02b90d8d8f))
- **guardrail**: add support for list of texts and aggregated GuardrailResult ([c9e9dda](https://github.com/thememium/dspy-guardrails/commit/c9e9ddaf648e527842f7206082d6147eb30cdbae))
- **example.py**: showcase Run() usage with single, batch, and early‑return examples ([d90ca6d](https://github.com/thememium/dspy-guardrails/commit/d90ca6dfeec5a065bed3cb33793a0da097b55b8b))
- **manager**: add deprecation warning for GuardrailManager ([f76371c](https://github.com/thememium/dspy-guardrails/commit/f76371c7d764810bf3fe66dc6169a3201baa6505))
- **guardrail**: add Run function to execute guardrails ([f59d5fa](https://github.com/thememium/dspy-guardrails/commit/f59d5faa87914d62060e4994ab20b7e9b3e143a1))
- **package**: expose guardrail module at top level ([5f3b8b7](https://github.com/thememium/dspy-guardrails/commit/5f3b8b70325603245f392d11bd244abe6c66bd9c))
- add guardrail module with factory functions for all guardrails ([aad5848](https://github.com/thememium/dspy-guardrails/commit/aad5848b7ccccef775089ac7453098ca70506557))
- **example.py**: migrate example to new guardrail module API ([de97e1d](https://github.com/thememium/dspy-guardrails/commit/de97e1d118fd278abc899a7a66ed2c261a443af7))
- **example.py**: configure guardrails with LM and clean up imports ([e483e22](https://github.com/thememium/dspy-guardrails/commit/e483e223600a739298040024b38ad06f855868ad))
- **notebooks**: add secret‑keys guardrail notebook ([9412fab](https://github.com/thememium/dspy-guardrails/commit/9412fab435507061fab528ba6f53d183d23460d7))
- **notebooks/006-keywords.py**: add keywords guardrail implementation ([155ccd4](https://github.com/thememium/dspy-guardrails/commit/155ccd423ae95838ec1796b98ac83103d100cdeb))
- **notebooks**: add 005-prompt-injection notebook for prompt‑injection analysis ([5a83ad1](https://github.com/thememium/dspy-guardrails/commit/5a83ad11a74022a03a764cbffb951109a90abc23))
- **notebook**: expose keywords_check as app function and split UI cells ([cfc1d76](https://github.com/thememium/dspy-guardrails/commit/cfc1d761faeae66d354c235f58de6a0a8473d9bd))
- **notebooks**: add keyword‑based guardrail notebook ([afe681e](https://github.com/thememium/dspy-guardrails/commit/afe681e91a67aebddc031ecd7f61ffa601161267))
- **notebooks**: add PII detection notebook with predefined patterns and UI ([b144a2c](https://github.com/thememium/dspy-guardrails/commit/b144a2cf97fecb14e504e430386a86ca9dcc7672))
- **notebooks**: add 003-jailbreak notebook for jailbreak detection ([4706386](https://github.com/thememium/dspy-guardrails/commit/4706386dec2a9ffebaa9135673afc7bf62d5c780))
- **notebooks**: add NSFW moderation notebook ([6a7ecda](https://github.com/thememium/dspy-guardrails/commit/6a7ecdab36738b00d167bcddada8ba7efa039ba3))
- **notebooks**: add 001-topic.py notebook for topic analysis with dspy and marimo ([c23fc3e](https://github.com/thememium/dspy-guardrails/commit/c23fc3e4c08a86b35faa58eeec54494afcd90232))

### 🩹 Fixes

- **config**: allow empty competitor_names in TopicGuardrailConfig ([75e0f00](https://github.com/thememium/dspy-guardrails/commit/75e0f00e1782a2c0dde0563571be41d5c088e238))
- **002-nsfw.py**: use dspy.Predict instead of ChainOfThought for Guardrails model ([b255306](https://github.com/thememium/dspy-guardrails/commit/b2553063037703e746595fa989765bc5977675fe))

### 💅 Refactors

- **tests**: drop unused guardrail imports from test_basic.py ([f5ebf43](https://github.com/thememium/dspy-guardrails/commit/f5ebf43e36f6250dc6128c83109ec8307b6545de))
- **001-topic.py**: rename business‑scope fields to generic topic‑scope fields ([0c5939c](https://github.com/thememium/dspy-guardrails/commit/0c5939ca65383d9ce41e231eb93ead6fe3cff250))
- **test**: rename TopicGuardrail config fields and simplify tests ([a053646](https://github.com/thememium/dspy-guardrails/commit/a0536467d4b5e48637a44b420279cb2da5005e24))
- **example.py**: rename guardrail.Topic parameters for clearer intent ([48b81ec](https://github.com/thememium/dspy-guardrails/commit/48b81ec0b1670e29c19d002d2df095f85a1ba8db))
- **guardrail**: rename business_scopes to topic_scopes and competitor_names to blocked_topics ([2744907](https://github.com/thememium/dspy-guardrails/commit/27449075ed5f0e7f82e0f08a95066e6b4e699a57))
- **topic**: rename business scope fields to topic scope and update guardrail ([2fec9d5](https://github.com/thememium/dspy-guardrails/commit/2fec9d534716852db833eecdc36cc19c0f67fd7e))
- **config**: rename TopicGuardrailConfig fields for clarity ([835fac5](https://github.com/thememium/dspy-guardrails/commit/835fac5e7b0effaba8d57dcfa012bf3115290c74))
- **guardrails**: standardize output field order across guardrail signatures ([2924bf3](https://github.com/thememium/dspy-guardrails/commit/2924bf38b3cec7cec53b15b719db61be9e1687f7))
- **tests**: replace guardrail function calls with class constructors ([5338641](https://github.com/thememium/dspy-guardrails/commit/5338641782028596aa282a92b6670fcad5126908))
- **guardrail**: remove deprecated function wrappers and warnings ([6a3bccc](https://github.com/thememium/dspy-guardrails/commit/6a3bccc3d3a2f93a6fdc654d853ee789bc79a659))
- **dspy_guardrails**: remove legacy factory exports from public API ([b333598](https://github.com/thememium/dspy-guardrails/commit/b3335982b43ed4ab8d6a0b0efbe423be055e11ea))
- **guardrail**: drop per‑guardrail LLM parameters ([666fd28](https://github.com/thememium/dspy-guardrails/commit/666fd281c27019f542d762d8ee2357efccd4e572))
- **core**: drop GuardrailManager import and export ([531dbc1](https://github.com/thememium/dspy-guardrails/commit/531dbc1f4b8e7467eace635b17ddd692866b00ab))
- **core/config.py**: centralize DSPy settings and simplify guardrail validation ([06812c4](https://github.com/thememium/dspy-guardrails/commit/06812c463bbbf467643ed1b510e67da28fe63ac6))
- **utils/dspy_config**: simplify DSPy configuration to use global LM ([981f820](https://github.com/thememium/dspy-guardrails/commit/981f820acb83b58afc0e769c8cffbc33b2c2be42))
- **guardrail**: return GuardrailResult directly for a single guardrail ([78dc3ed](https://github.com/thememium/dspy-guardrails/commit/78dc3ed0c68e2a88bc98a3da7c3a7ec886044e2a))
- **example.py**: simplify single guardrail execution ([e5cca16](https://github.com/thememium/dspy-guardrails/commit/e5cca16f13ec7f484372d1ed08273f13a3cfac59))
- **tests**: make Run always return a list of GuardrailResult ([b36ce02](https://github.com/thememium/dspy-guardrails/commit/b36ce021b37fd9e499f2286935394cbd924aaccc))
- **example.py**: unify guardrail testing with bulk Run ([91f3920](https://github.com/thememium/dspy-guardrails/commit/91f392041e6d3275647666f3d35aef282fc31f64))
- **guardrail**: always return List[GuardrailResult] from Run() ([e9abeca](https://github.com/thememium/dspy-guardrails/commit/e9abecaa27dfbf17c924c7e40eef4d667172e735))
- **example.py**: replace direct Run import with guardrail.Run ([a42330c](https://github.com/thememium/dspy-guardrails/commit/a42330cd4619bbf4cf40d73ba60488201eae5787))
- **__init__**: clean up public API and expose Run ([8f867be](https://github.com/thememium/dspy-guardrails/commit/8f867be9e98e3c98728b6bb26e7343df68bde930))
- **factory**: remove create_comprehensive_guardrail_suite function ([bb5775a](https://github.com/thememium/dspy-guardrails/commit/bb5775aebdb2484df8122d5bd48121a85485c6c4))
- **007-secret-keys**: make detection functions synchronous and drop asyncio ([c5996c7](https://github.com/thememium/dspy-guardrails/commit/c5996c7f4d74af44f0a2aba1502e3297b507660d))
- **006-keywords.py**: restructure output assembly and improve line formatting ([c04a477](https://github.com/thememium/dspy-guardrails/commit/c04a477029f62258f9fe8510f464d01cccd49744))
- **keywords**: improve readability and add test harness for guardrail ([55049c1](https://github.com/thememium/dspy-guardrails/commit/55049c1e2f1c7237b944feb8937e809979f49e97))
- overhaul jailbreak signature with taxonomy and new field names ([5b3637d](https://github.com/thememium/dspy-guardrails/commit/5b3637d4fe63bb5f8f03173c90143c8c89b27d0c))
- **005-keywords**: assemble markdown via parts list for clearer generation ([e333805](https://github.com/thememium/dspy-guardrails/commit/e333805fc23f4899f327a625d23d27a3e2592b71))
- **keywords**: simplify regex handling and clean up UI cells ([f19d9fe](https://github.com/thememium/dspy-guardrails/commit/f19d9fe83c783ec34f673045e021f80678917157))
- **001-topic.py**: rename TopicSignature to GuardrailsTopicSignature and inline program creation ([3f8ca38](https://github.com/thememium/dspy-guardrails/commit/3f8ca3845479ed58fcf58377fe6549f77550043b))
- **notebooks/002-nsfw.py**: rename fields for NSFW detection ([247982d](https://github.com/thememium/dspy-guardrails/commit/247982d3af90f722666b9acb1dbb0d7e71576088))

### 📖 Documentation

- add RalphSpec integration docs and .ralphspec ignore entry ([40bdf45](https://github.com/thememium/dspy-guardrails/commit/40bdf45d0aeffe94232f7d1c076bd138f06da709))
- **readme**: add new guardrail types and update navigation ([2eabe2e](https://github.com/thememium/dspy-guardrails/commit/2eabe2ef5fe7c8767256ffd44bebe2e86e190c08))
- **quickstart**: add examples for PII allowed types, Toxicity, Tone, Grounding ([3f96d68](https://github.com/thememium/dspy-guardrails/commit/3f96d68ca6751a147aa05541d0162bfcbd56d607))
- **spec**: update QUICKSTART references to new docs path ([47cbbdd](https://github.com/thememium/dspy-guardrails/commit/47cbbddae92c6602d66b10244b672470aa476e63))
- **readme**: update guide links and add migration guide references ([41d4f95](https://github.com/thememium/dspy-guardrails/commit/41d4f95460d7a75c4d5e80e59b584200d0175014))
- fix relative README.md links in migration guide and quickstart ([d27c568](https://github.com/thememium/dspy-guardrails/commit/d27c56883c81ce81a4bf6f857448e174c2416a0d))
- add Migration Guide and Quickstart documentation ([2de9891](https://github.com/thememium/dspy-guardrails/commit/2de989171eb17cc39f65676732c149b5fa1ec033))
- **migration-guide**: update guide for Topic guardrail renaming and API changes ([935932a](https://github.com/thememium/dspy-guardrails/commit/935932a31bd28a95536c6edfff45cf5e7cd33ffb))
- **readme**: rename business_scopes to topic_scopes ([bd7ba33](https://github.com/thememium/dspy-guardrails/commit/bd7ba330485b00da0084ddcb41ac5676061dbf09))
- **quickstart**: update guardrail method names to match new API ([18d051a](https://github.com/thememium/dspy-guardrails/commit/18d051a517eaa5aa42beb7556d1686b2263666e1))
- **example.py**: update usage to class‑based API ([14ba297](https://github.com/thememium/dspy-guardrails/commit/14ba29711e0fae065ac69e021753845e6257202e))
- **readme**: capitalize guardrail helper names in examples ([55099d2](https://github.com/thememium/dspy-guardrails/commit/55099d2eaf0ddd8bdfc71075665535bf1b5cfedf))
- **quickstart**: add QUICKSTART.md with step‑by‑step guide for DSPy Guardrails ([4189e59](https://github.com/thememium/dspy-guardrails/commit/4189e596d57bd230163f7d9fbe3e40bb88e00972))
- **readme**: add multiple texts execution examples and update feature list ([a72c85e](https://github.com/thememium/dspy-guardrails/commit/a72c85e05da8fa12e80a8a7b54332611c304ce75))
- overhaul migration guide for production release ([5c7e0af](https://github.com/thememium/dspy-guardrails/commit/5c7e0af24c5c2769ff9f40822f5f2a35a8ddef8a))
- **readme**: remove factory functions and GuardrailManager migration guide ([b903f06](https://github.com/thememium/dspy-guardrails/commit/b903f06526f180cc161beaa42c04a562ba272878))
- **readme**: simplify single guardrail execution example and clarify return type ([2976c3b](https://github.com/thememium/dspy-guardrails/commit/2976c3b1262e69a1ae92a1c35eaad2f5acf3bfb2))
- **MIGRATION_GUIDE**: add Run API return type section and restructure guide ([da16e6b](https://github.com/thememium/dspy-guardrails/commit/da16e6bec61cdee81eeb3f78bee52a4203342ad8))
- add CHANGELOG.md documenting breaking change in guardrail.Run ([2152167](https://github.com/thememium/dspy-guardrails/commit/2152167746bee2935dbd045d9fa4ec9cd386fcd6))
- **package-api**: enforce Run() to always return List[GuardrailResult] ([8d4aec1](https://github.com/thememium/dspy-guardrails/commit/8d4aec1243b90bc58d2252c1e0e9b2228e64653a))
- **readme**: replace simple usage with bulk Run examples and clarify API ([a03b878](https://github.com/thememium/dspy-guardrails/commit/a03b878e6cfbef3188d1e7e13920025347a992b1))
- **readme**: update examples to use guardrail.Run ([7ec8a92](https://github.com/thememium/dspy-guardrails/commit/7ec8a92d4aa7da3418315ca6029a4c1c221d8464))
- **guardrail.py**: update examples to use fully qualified guardrail.Run ([6f8c446](https://github.com/thememium/dspy-guardrails/commit/6f8c446d873477e50f271a1137662cc04140aa60))
- **readme**: replace GuardrailManager examples with Run() function and add migration guide ([6f603b9](https://github.com/thememium/dspy-guardrails/commit/6f603b9fbf6b00d9654301cb9c1a67893cbcf803))
- **readme**: update configuration instructions and usage examples ([1d1fc19](https://github.com/thememium/dspy-guardrails/commit/1d1fc19b7953bc52e8a5247c0a4bf88400951e36))
- add migration guide for DSPy configuration changes ([f8f1bc9](https://github.com/thememium/dspy-guardrails/commit/f8f1bc959dcb09355ab20aea8aec03f34e8e3e7a))
- **AGENTS.md**: add DSPy configuration requirement to environment setup ([b30db29](https://github.com/thememium/dspy-guardrails/commit/b30db29689fdcf236999f9cd034d9467509710f4))
- **example**: add example usage script for DSPy Guardrails ([f0060d8](https://github.com/thememium/dspy-guardrails/commit/f0060d8fea368c0f98f75b4569e00a920519e121))
- **readme**: add Python package usage examples ([c53f90f](https://github.com/thememium/dspy-guardrails/commit/c53f90f40c1607b392d3013d9805abe0e185fb20))
- **AGENTS.md**: add OpenSpec managed block, project overview, and updated guidelines ([e4b20d1](https://github.com/thememium/dspy-guardrails/commit/e4b20d15a2d3d1360f192b2666431ed5db8fab0d))
- add OpenSpec command templates ([17b2bfe](https://github.com/thememium/dspy-guardrails/commit/17b2bfefb39ee59b7b17f98102ec24dfcf68ff28))
- **readme**: remove unused logo image and broken GitHub link ([0b28c0f](https://github.com/thememium/dspy-guardrails/commit/0b28c0f48c5c8e0d0b7558da3af12b27de87a59c))
- **readme**: add comprehensive project overview and usage guide ([2fc83db](https://github.com/thememium/dspy-guardrails/commit/2fc83dbaf427dfcacbc91207e3a1766c9e4f54b2))
- **AGENTS.md**: add agent guidelines and development workflow documentation ([28f3131](https://github.com/thememium/dspy-guardrails/commit/28f3131f1ccb6c4cfac06eb2fb3eb87d2000dcd7))

### 🏡 Chore

- **pyproject**: simplify production deps and enrich dev tooling ([44fd7fb](https://github.com/thememium/dspy-guardrails/commit/44fd7fb40b2cbd0b09534fa2550d68bedd51da02))
- **pyproject**: update clean task to target src and add deptry checks ([371629d](https://github.com/thememium/dspy-guardrails/commit/371629d7f9b4bffe88034d6ed97141477bb60fe6))
- **gitignore**: add .tree to ignore list ([96e7736](https://github.com/thememium/dspy-guardrails/commit/96e7736aaedcf45cb41641b29f0d54f703f3f348))
- **dspy_guardrails**: delete unused factory module ([613ff44](https://github.com/thememium/dspy-guardrails/commit/613ff44f1baa33673188ea6c446820a861f6da5c))
- **dspy_guardrails**: remove deprecated GuardrailManager ([34b898f](https://github.com/thememium/dspy-guardrails/commit/34b898fe3cbf668350766483aab38ba09a9c3ed0))
- **pyproject**: restructure metadata formatting and narrow clean task scope ([2514b90](https://github.com/thememium/dspy-guardrails/commit/2514b90401ce9f629e1eb5bc77bc8ce23f163106))
- **pyproject**: add authors, keywords, classifiers, and setuptools package discovery ([79c4a41](https://github.com/thememium/dspy-guardrails/commit/79c4a416e7b13b04497f7b23e168e366955886ad))
- **pyproject**: reformat dependencies list and tidy dev group ([f1c9470](https://github.com/thememium/dspy-guardrails/commit/f1c94703e51250e1a3eec9a6d0df6b8501ea82d1))
- **notebooks**: replace old keyword notebook with new placeholder ([7353985](https://github.com/thememium/dspy-guardrails/commit/7353985f642a86f392336843043153c7cae3cdb9))
- **pyproject**: add dev dependency group and poe task definitions ([3ad55cb](https://github.com/thememium/dspy-guardrails/commit/3ad55cbba673cbf4d51094e9bb951cd652b1ca09))

### ✅ Tests

- **guardrails**: add tests for grounding and newly introduced guardrail classes ([7d19f9a](https://github.com/thememium/dspy-guardrails/commit/7d19f9a35a0c25b786e498c3e9db4692a81224b3))
- **Run**: add extensive tests for aggregated GuardrailResult and metadata handling ([59a901a](https://github.com/thememium/dspy-guardrails/commit/59a901ae736d4fd35019fdf40a0ccabcfa523b2c))
- remove deprecated GuardrailManager migration and config validation tests ([cdb155e](https://github.com/thememium/dspy-guardrails/commit/cdb155e6a813735538ce549bd04ec2811b6f4675))
- update Run tests to reflect return type logic and add new test ([81151a4](https://github.com/thememium/dspy-guardrails/commit/81151a49f57e7e2b9bd0695510c92ceecb90071a))
- migrate guardrail manager tests to Run() and add Run API coverage ([770f857](https://github.com/thememium/dspy-guardrails/commit/770f8575bcf80bbcbdffeb469ca2d973067a9f6b))
- **guardrail**: add comprehensive unit tests for guardrail module ([d4a77cb](https://github.com/thememium/dspy-guardrails/commit/d4a77cb8c8059dde3229d5eefeaf47a0bd5e2589))
- **tests**: add guardrail configuration tests and pytest fixture ([c6d01fe](https://github.com/thememium/dspy-guardrails/commit/c6d01fe036167f5cfcc2f830fd381d08b4fb716a))
- **tests**: add basic unit tests for guardrail package ([1ab5825](https://github.com/thememium/dspy-guardrails/commit/1ab5825012bfff8d94296b07c9d1f48c1027531b))

### 🎨 Styles

- **tests**: reformat import statements for readability and consistency ([85fe932](https://github.com/thememium/dspy-guardrails/commit/85fe93262b7d1884b1cb23eb768857d74431425d))
- **dspy_guardrails**: reformat import statements for readability ([19f1a1e](https://github.com/thememium/dspy-guardrails/commit/19f1a1ef49c555d612debcf4ae59c5eec2ab351b))
- **notebooks**: reorder imports for consistency and readability ([0f082b5](https://github.com/thememium/dspy-guardrails/commit/0f082b547583328beaee3fabff85585a43cbdcaf))
- **005-keywords.py**: reformat keyword handling & regex boundaries ([dd49804](https://github.com/thememium/dspy-guardrails/commit/dd4980443b90bdb3342e35e62a0b0bb872980514))
- **notebooks**: reorder imports and tidy whitespace for consistency ([6235985](https://github.com/thememium/dspy-guardrails/commit/62359853393583887a9aeeddc3428a98128d6e69))

### Other Changes

- Merge pull request #1 from thememium/feat/convert-to-package (#1) ([4203fe9](https://github.com/thememium/dspy-guardrails/commit/4203fe9d8b9034f462407f1b95e5788727762ff3))

### Contributors

- Edward Boswell <thememium@gmail.com>
- Edward Boswell <edward.boswell@auctane.com>

## [Unreleased]

### Changed

- **BREAKING**: `guardrail.Run()` now returns a single `GuardrailResult` when passed a single guardrail, instead of a list. Multiple guardrails still return a `List[GuardrailResult]`. This eliminates the need for `[0]` indexing when using single guardrails.
