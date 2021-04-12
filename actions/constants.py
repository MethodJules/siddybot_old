
# Klasse für die Speicherung von Konstanten
class Constants():

   #### Attribute der Organisationen:
   #
   # Alle Attribute zu Organisation
   organization_attributes = ["city_of_headquarters","employee_or_member_of", "top_members_employees", "schools_attended", "member", "country_of_headquarters",
                               "date_founded", "founded_by", "political_religious_affiliation", "stateorprovince_of_headquarters", "subsidiares", "headquarter", "founded", "biographie"]
   #
   # Attribute zur Abfrage des Hauptsitzes
   headquarter_attribute = ["city_of_headquarters", "stateorprovince_of_headquarters", "country_of_headquarters", "biographie"]
   #
   # Einzelne Attribute der Organisationen 
   subsidiares = "subsidiares" 
   political_religious_affiliation = "political_religious_affiliation"
   city_of_headquarter = "city_of_headquarters"
   country_of_headquarter = "country_of_headquarters"
   stateorprovince_of_headquarter = "stateorprovinces_of_headquarters"
   employee_or_member = "employee_or_member_of"
   top_employee_member = "top_members_employees"
   schools_attended = "schools_attended"
   date_founded = "date_founded"
   founded_by = "founded_by"
   founded = "founded"
   member = "member"
   headquarter = "headquarter"
   biographie = "biographie"

   #### Attribute Personen
   #
   # Alle Attribute zu Personen
   person_attributes = ["age", "alternate_name", "cause_of_death", "children", "cities_of_residence",
                       "city_of_birth", "city_of_death", "siblings", "countries_of_residence", "country_of_birth",
                       "country_of_death", "date_of_birth", "date_of_death", "employee_or_member_of", "spouse",
                       "founded_by", "origin", "other_family", "parents", "religion", "schools_attended", 
                       "stateorprovince_of_residence", "title", "top_members_employees", "birthplace",  "death_place", "residences",
                       "family", "member", "biographie", "death", "birth"]
   #
   # Attribute fuer Aufenthaltsorte 
   residence_attribute = ["stateorprovince_of_residence", "countries_of_residence", "cities_of_residence"]
   #
   # Attribute fuer Zugehoerigkeit zu Organisationen 
   members = ["employee_or_member_of", "top_members_employees", "schools_attended"]
   #
   # Attribute zur Abgefrage von Familienmitgliedern
   family_attribute = ["parents", "other_family", "spouse", "siblings", "children"]
   #
   # Einzelne Attribute von Personen
   residences = "residences"
   date_of_birth = "date_of_birth"
   birthplace = "birthplace"
   city_of_birth = "city_of_birth"
   country_of_birth = "country_of_birth"
   country_of_death = "country_of_death"
   city_of_death = "city_of_death"
   deathplace = "death_place"
   date_of_death = "date_of_death"
   cause_of_death = "cause_of_death"
   cities_of_residence = "cities_of_residence"
   countries_of_residence = "countries_of_residence"
   sibling = "siblings"
   children = "children"
   spouse = "spouse"
   other_family = "other_family"
   parents = "parents"
   family = "family"
   title = "title"
   origin = "origin"
   alternate_name = "alternate_name"
   stateorprovince_of_residence = "stateorprovince_of_residence"
   religion = "religion"
   death = "death"
   birth = "birth"

   # Konstanten aus der Rueckgabe von der Datenbank
   ent2_text = "ent2_text"
   ent2_ner = "ent2_ner"
   ent_ner = "ent_ner"
   entities_relation = "entities_relations"
   relationship = "rel"
   ent_text = "ent_text"
   result = "result"
   types = "types"
   node_title = "node_title"
   sents = "sents"
   entities = "entities"
   root_nodes = "root_nodes"
   node_count = "node_count"
   node_id = "node_id"

   # Slotnamen
   slot_attribute = "attribute"
   slot_org = "ORG" 
   slot_object_type = "object_type"
   slot_cardinal = "CARDINAL"
   slot_person = "PERSON"
   slot_place = "GPE"
   slot_country = "COUNTRY"
   slot_city = "CITY"
   slot_entity_not_found = "entity_not_found"
   slot_shall_explain_add_person = "shall_explain_add_person"
   slot_explained_add_person = "explained_add_person"
   slot_religion = "RELIGION"
   slot_shall_explain_add_entity = "shall_explain_add_entity"
   slot_last_link = "last_link"
   slot_explained_add_entity = "explained_add_entity"
   slot_username = "username"
   slot_age = "age"
   slot_expert_value = "expert_value"
   slot_gender = "gender"
   slot_semantic_search_result = "semantic_search_result"
   slot_shall_explain_add_entity = "shall_explain_add_entity"
   slot_shall_explain_add_person = "shall_explain_add_person"

   #### In den Actions relevante Objekttypen
   #
   # Einzelne Objekttypen
   organization = "ORGANIZATION"
   person = "PERSON"
   cause = "CAUSE"
   city = "CITY"
   country = "COUNTRY"
   place = "PLACE"
   date = "DATE"
   state_or_province = "STATE_OR_PROVINCE"
   cause_of_death = "CAUSE_OF_DEATH"
   profession = "PROFESSION"
   nationality = "NATIONALITY"
   location = "LOCATION"
   title = "TITLE"
   ideology = "IDEOLOGY"
   #
   # Objekttypen der Webseite
   object_types = [organization, person, cause_of_death, city, country, state_or_province, profession, nationality, location, title, ideology]




