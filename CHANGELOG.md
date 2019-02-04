# Kids First Dataservice Release 1.9.0

## Features

### Summary

Feature Emojis: 🐛🗃x1 ♻️x1
Feature Labels: [data model](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/data%20model) x1 [feature](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/feature) x1

### New features and changes

- (#497) 🐛🗃 Migration - Fix sequencing_experiment_genomic_file KF ID prefixes - @znatty22
- (#492) ♻️ Make Seq Exp and Genomic File Many to Many - @znatty22


# Kids First Dataservice Release 1.8.0

## Features

### Summary

Feature Emojis: ✨x1
Feature Labels: [data model](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/data%20model) x1 [feature](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/feature) x1

### New features and changes

- (#486) ✨ Add access_urls to indexd models to point to gen3 locations - @dankolbman


# Kids First Dataservice Release 1.7.0

## Features

### Summary

Feature Emojis: x1 🐛x1 ✨x1 🎨x1 🚚x1
Feature Labels: [feature](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/feature) x2 [bug](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/bug) x2 [refactor](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/refactor) x2 [documentation](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/documentation) x1

### New features and changes

- (#473)  ✨Add biospecimen_id and genomic_file_id for genomic file and biospecimen endpoint - @parimalak
- (#480) 🐛 Do not include 'None' in rollup arrays - @dankolbman
- (#478) ✨ Summarize sequencing experiment fields on genomic file - @dankolbman
- (#476) 🎨 Make capitalization consistent for resources - @dankolbman
- (#474) 🚚 Mass rename of CavaticaTask and relationships - @dankolbman


# Kids First Dataservice Release 1.6.0

## Features

### Summary

Feature Emojis: 🐛x1 🔧x1 ✨x1
Feature Labels: [feature](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/feature) x2 [bug](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/bug) x1 [data model](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/data%20model) x1

### New features and changes

- (#471) 🐛 Fix typo in license badge link - @znatty22
- (#469) 🔧 Update Biospecimen method_of_sample_procurement enum - @znatty22
- (#468) ✨ Add method_of_sample_procurement col to biospec - @znatty22


# Kids First Dataservice Release 1.5.0

## Features

### Summary

Feature Emojis: ♻️x2 ⬆️x1 🐛x1 🔥x1
Feature Labels: [refactor](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/refactor) x1

### New features and changes

- (#458) ⬆️ Upgrade dependencies - @dankolbman
- (#459) 🐛 Fix down rev in migration - @znatty22
- (#455) ♻️ Standardize biospecimen_diagnosis entity - @znatty22
- (#453) ♻️ Standardize read_group_genomic_file entity - @znatty22
- (#456) 🔥 Remove cascade delete genomic file on sequencing-experiment delete - @znatty22


# Kids First Dataservice Release 1.4.0

## Features

Patches breaking change for Indexd and moves consent field from
participant to biospecimen.

### Summary

Feature Emojis: x1 ♻️x1
Feature Labels: [refactor](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/refactor) x2 [data model](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/data%20model) x1 [bug](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/bug) x1

### New features and changes

- (#447)  ✨Move consent_type from participant to biospecimen - @parimalak
- (#443) ♻️ Don't use rev in indexd requests - @dankolbman


# Kids First Dataservice Release 1.3.3

## Features

### Summary

Feature Emojis: 🐛x1
Feature Labels: [bug](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/bug) x1

### New features and changes

- (#439) 🐛 Remove duplicates from join results - @dankolbman


# Kids First Dataservice Release 1.3.2

## Features

- (#437) 🐛 Fix join for genomic files study filter - @dankolbman


# Kids First Dataservice Release 1.3.1

## Features

### Summary

Feature Emojis: ✨x5 🐛x2 🔧x1
Feature Labels: [feature](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/feature) x3 [bug](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/bug) x2 [refactor](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/refactor) x2 [data model](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/data%20model) x1

### New features and changes

- (#436) ✨update outcome enum to deceased - @parimalak
- (#420) 🐛 fix parsing of uniqueness constraint error - @fiendish
- (#435) 🔧 Update read group quality scale enum - @znatty22
- (#430) ✨ Update analyte_type enum to support imaging files - @parimalak
- (#427) 🐛 Fix filtering in biospecimen, diagnosis GET all endpoint - @znatty22
- (#412) ✨ Refactor ReaGroup GenomicFile Relation - @znatty22
- (#426)  ✨ Update data_type enum to support image files - @parimalak
- (#422) ✨Rename field volume_ml to volume_ul - @parimalak


# Kids First Dataservice Release 1.3.0

## Features

Adds several new fields in the datamodel in #408:

- `family_type` on Family
- `source_text_notes` on FamilyRelationship
- `affected_status` on Participant
- `diagnosis_category` on Participant
- `visible` on all tables

### Summary

Feature Emojis: ✨x4 👷x1 🔧x1 🐛x1
Feature Labels: [data model](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/data%20model) x4 [devops](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/devops) x3 [feature](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/feature) x3

### New features and changes

- (#416) 🐛 Fix biospecimens and diagnoses links by diagnosis_id and biospecimen_id - @parimalak
- (#413) 👷 Load bucket url from vault - @dankolbman
- (#401) ✨ Add biospecimen_diagnosis association table - @parimalak
- (#410) 🔧 Increase nginx proxy_buffer size to stop truncating repsonses - @dankolbman
- (#408) ✨Data model changes - @parimalak
- (#407) ✨ Add visible to base model - @parimalak
- (#394) ✨ Add biospecimen_genomic_file association table and endpoints - @parimalak


# Kids First Dataservice Release 1.2.0

## Features

### Summary

Feature Emojis: ✨x3 🐛x3 👷x1
Feature Labels: [bug](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/bug) x3 [data model](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/data%20model) x2 [data-import](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/data-import) x1 [devops](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/devops) x1 [documentation](https://api.github.com/repos/kids-first/kf-api-dataservice/labels/documentation) x1

### New features and changes

- (#389) ✨ Add More than One Race to race enum - @parimalak
- (#386) 🐛 Fix sns mocks - @dankolbman
- (#384) 👷 Added new jenkinsfile - @alubneuski
- (#359) ✨ Add relation from biospecimen to diagnosis - @dankolbman
- (#352) ✨ Read groups - @dankolbman
- (#373) 🐛 Fix 500 error on /studies?study_id - @znatty22
- (#380) 🐛 Update API docs - correct version of code - @znatty22


# Kids First Dataservice Release v1.1.0

## Features
### Summary

Feature Emojis: ✨x17 🐛x10 🗃x5 🔧x3 📝x2 ⚡x2 👷x1 💄x1 🚑x1 🏷x1 ♻️x1
Feature Labels: [data model](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"data+model"+) x17 [feature](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"feature"+) x12 [bug](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"bug"+) x12 [Ready for review](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"Ready+for+review"+) x5 [refactor](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"refactor"+) x3 [documentation](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"documentation"+) x2 [devops](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"devops"+) x1
### New features and changes

- (#316) 🔧 Bucket secret default - @dankolbman
- (#317) ✨ Basic Filter Params - @znatty22
- (#324) ♻️ Refactor child links - @znatty22
- (#331) 🔧Fix reverse family relationships - @znatty22
- (#333) 🐛 Fix case sensitivity of family relationships - @znatty22
- (#299) ✨ Add enum validators for entities - @parimalak
- (#279) ✨ Add SNS events for data changes - @dankolbman
- (#334) ✏️ Update genomic file data type enum - @dankolbman
- (#335) 🐛 Default SNS ARN to None - @dankolbman


# Kids First Dataservice Release v1.0.0

## Features
### Summary

Feature Emojis: ✨x14 🐛x8 🗃x5 📝x2 ⚡x2 👷x1 💄x1 🔧x1 🚑x1
Feature Labels: [data model](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"data+model"+) x16 [bug](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"bug"+) x10 [feature](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"feature"+) x9 [Ready for review](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"Ready+for+review"+) x2 [documentation](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"documentation"+) x2 [refactor](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"refactor"+) x1
### New features and changes

- (#145) ✨ Genomic file resource - @dankolbman
- (#196) ✨ Alias Group Model (for participant aliases) - @znatty22
- (#204) ✨Model updates - @parimalak
- (#218) ✨ Merging participant and demographic - @parimalak
- (#219) 👪 Family model and resources - @dankolbman
- (#223) 📝 Update API docs to include 400, 404 responses - @znatty22
- (#225) 👷 moving to the new deployment process - @alubneuski
- (#228) ✨Biospecimen model - @parimalak
- (#230) ✨ Filter Resources by Study  - @znatty22
- (#235) 🐛 fix backref's for diagnoses, outcomes, phenotypes in participant model - @parimalak
- (#238) 🗃 Add missing alias_group migration - @znatty22
- (#244) ✨ Sequencing Center entity - @parimalak
- (#247) 🗃 Fix migration heads - @parimalak
- (#250) ⚡️Optimize loading of children in default pagination - @znatty22
- (#252) 💄 Center logo and badges - @dankolbman
- (#253) 🗃 Study file integration with Indexd - @dankolbman
- (#255) 🐛 Use correct schema for study file resources - @dankolbman
- (#256) 📝 Update entity relationship diagram - @znatty22
- (#258) 🐛Delete parent orphans - @znatty22
- (#261) ✨ Relation links - @znatty22
- (#262) ✨Model Changes - @parimalak
- (#263) ✨ Add integration with bucket service - @dankolbman
- (#268) 🔧 Update indexd required fields with required flag in schema - @znatty22
- (#270) ✨ Add availabilty to study_file - @parimalak
- (#281) 🗃 Squash migrations - @dankolbman
- (#283) 🐛 Change modified_at field on update - @dankolbman
- (#284) ⚡️ Faster tests - @dankolbman
- (#289) ✨ Update sequencing_experiment_id to be nullable in genomic_file - @parimalak
- (#290) ✨ Cavatica Models and Endpoints - @znatty22
- (#300) 🐛 Fix bug w shipment_date = null - @znatty22
- (#302) 🗃 Remove null constraint on biospecimen_id in genomic file - @dankolbman
- (#304) 🐛 Fix bug w experiment_date = null - @znatty22
- (#305) ✨ Move acl to root document - @dankolbman
- (#308) 🐛 Use the db session by default in all base schemas - @dankolbman
- (#309) 🐛 Ignore mime type when parsing request body - @dankolbman
- (#312) 🚑 Remove datamodel and migration version from status - @dankolbman


# Kids First Dataservice Release 0.2.0

### Summary

Feature Emojis: ✨x38 👷x10 🐛x10 ♻️x6 📝x5 🗃x3 🐳x2 🔧x2 Nonex2 💥x1 🐘x1 🖼x1 🔥x1 🚢x1 🏷x1 🕷x1
Feature Labels: [feature](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"feature"+) x24 [data model](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"data+model"+) x22 [refactor](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"refactor"+) x9 [bug](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"bug"+) x9 [devops](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"devops"+) x8 [documentation](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"documentation"+) x3 [Epic](https://github.com/kids-first/kf-api-dataservice/issues?utf8=%E2%9C%93&q=label%3A"Epic"+) x1

### New features and changes

- (#10) ✨ Create person entity - @dankolbman
- (#15) 👷 Add Jenkinsfile - @dankolbman
- (#17) 🐳 Add docker file - @dankolbman
- (#23) 🗃 Add base mixin for the data model - @dankolbman
- (#26) 🔧 Refactor code base to be modular for additional entities - @znatty22
- (#27) ✨ Kids First Ids - @dankolbman
- (#30) ♻️ Formatting responses and abstracting out some of the models - @dankolbman
- (#31) 📝 Update readme with information - @dankolbman
- (#33) 👷 Add CircleCI tests - @dankolbman
- (#34) 👷 Add badge for CircleCI - @dankolbman
- (#37) 🐛 Fix circleci - @dankolbman
- (#38) 🐛 Update/fix Base class in models.py - @znatty22
- (#49) 🔧 Update sqlalchemy config w foreign key constraint for sqlite - @znatty22
- (#54) 🐛 Initialize database on start - @dankolbman
- (#56) ✨ Status page and rerouting - @dankolbman
- (#60) ♻️ Rename Person to Participant in all relevant files - @znatty22
- (#61) ✨ Add ERD generator - @dankolbman
- (#62) ✨ Demographic resource and tests - @znatty22
- (#64) ✨ Add Demographic db model - @znatty22
- (#65) 💥 Nuke and pave™ - @dankolbman
- (#66) ✨ Sample db model - @parimalak
- (#67) ✨ Add Diagnosis db model and tests - @znatty22
- (#72) ✨ Deserialize objects - @dankolbman
- (#73) 📝 swagger docs - @dankolbman
- (#74) ✨ Aliquot model with Tests - @parimalak
- (#75) ✨ Diagnosis resource and tests - @znatty22
- (#77) ✨ Add pagination - @dankolbman
- (#78) 🐘 Postgres - @dankolbman
- (#79) ✨ Genomic file model and tests - @znatty22
- (#81) ✨ Add Sequencing experiment model with tests - @parimalak
- (#82) ✨ Sample resource and tests - @znatty22
- (#84) ✨ Aliquot resource - @znatty22
- (#85) ♻️ Refactor pg exceptions to flask error handler - @dankolbman
- (#88) ♻️ Refactor dummy data generator - @znatty22
- (#89) ✨ Dummy data generator - @parimalak
- (#91) 👷 Fix dependency bug for CircleCI - @dankolbman
- (#96) 🐛 Change hvac requirement back to http - @dankolbman
- (#97) 👷 Update deploy to QA in Jenkinsfile - @dankolbman
- (#98) 🐛 Fix typo in Jenkins file - @dankolbman
- (#99) 🐛 Add line break - @dankolbman
- (#100) 🐛 Fix Jenkinsfile typo - @dankolbman
- (#102) 👷 Feature/simplifying jenkinsfile - @alubneuski
- (#103) 📝 Update README with how to generate mock data - @dankolbman
- (#105) 🗃 Remove postgres id and use kf_id as primary key - @dankolbman
- (#107) 🗃 Change uuid field to Postgres UUID - @dankolbman
- (#109) ✨ Add Controlled Access field to Genomic file entity - @parimalak
- (#114) ✨ Family relationship model - @znatty22
- (#121) ✨ Phenotype model - @parimalak
- (#125) ✨ Add Outcome Entity to Model - @parimalak
- (#126) ✨ Workflow model - @znatty22
- (#130) ✨ Study model - @znatty22
- (#131) ✨ Add fields to diagnosis Entity - @parimalak
- (#132) ✨ Add fields to Partcipant Entity - @parimalak
- (#135) ✨ Kf id prefix - @dankolbman
- (#139) 👷 Feature/add clean before checkout - @alubneuski
- (#144) 👷 Removed clean before checkout - @alubneuski
- (#146) ✨ Add Investigator model - @parimalak
- (#149) ✨ Study file model - @parimalak
- (#155) ✨ Add file_size to GenomicFile model - @znatty22
- (#157) 🖼 Readme image - @dankolbman
- (#158) 🐛 Fix self links - @dankolbman
- (#159) 📝 add NOTICE - @allisonheath
- (#170) 👷 Add codacy integration - @dankolbman
- (#173) ✨ ⚡️Change PUT to PATCH in all resource APIs and minor updates - @znatty22
- (#174) ✨ Add pagination to resources - @dankolbman
- (#175) ✨ Study resource - @dankolbman
- (#176) ✨ Investigator resource - @dankolbman
- (#177)  🔒 Avoid system calls during status request - @dankolbman
- (#178) ♻️ Rename participant tests to conform to naming convention - @dankolbman
- (#179) 🔥 Remove SQLite configuration - @dankolbman
- (#180) ✨ Add phenotype endpoint - @parimalak
- (#181) 👷 Added jenkins webhook property - @alubneuski
- (#183) ♻️ Fix self links - @dankolbman
- (#186) 📝 Docs branding - @dankolbman
- (#189) ✨Add outcome endpoint - @parimalak
- (#190) ✨ Sequencing Experiment Resource - @znatty22
- (#194) ✨Family relationship resource - @znatty22
- (#195) 🚢 Added prd deployment step without tagging - @alubneuski
- (#197) ✨Study file resource - @parimalak
- (#200) 🐳 Use nginx for main proxy - @dankolbman
- (#203) 🏷 Feature/adding tagging - @alubneuski
- (#206) ☁️ Added cloud region - @alubneuski
- (#214) 🕷fixing - @alubneuski
- (#215) 🐛 Put back dockerfile command - @dankolbman
- (#216) 🐛 Use run script to upgrade db before supervisor - @dankolbman
