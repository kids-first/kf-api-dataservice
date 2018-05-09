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
