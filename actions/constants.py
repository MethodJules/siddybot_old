
class Constants():

   # Attribute der Organisationen:
   organization_attributes = ["city_of_headquarters","employee_or_member_of", "top_members_employees", "schools_attended", "member", "country_of_headquarters",
                               "date_founded", "founded_by", "political_religious_affiliation", "stateorprovince_of_headquarters", "subsidiares", "headquarter", "founded", "biographie"]
   headquarter_attribute = ["city_of_headquarters", "stateorprovince_of_headquarters", "country_of_headquarters", "biographie"]
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

   #Attribute Personen
   person_attributes = ["age", "alternate_name", "cause_of_death", "children", "cities_of_residence",
                       "city_of_birth", "city_of_death", "siblings", "countries_of_residence", "country_of_birth",
                       "country_of_death", "date_of_birth", "date_of_death", "employee_or_member_of", "spouse",
                       "founded_by", "origin", "other_family", "parents", "religion", "schools_attended", 
                       "stateorprovince_of_residence", "title", "top_members_employees", "birthplace",  "death_place", "residences",
                       "family", "member", "biographie", "death", "birth"]
   residence_attribute = ["stateorprovince_of_residence", "countries_of_residence", "cities_of_residence"]
   members = ["employee_or_member_of", "top_members_employees", "schools_attended"]
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

   # 2. Knoten der Rueckgabe:
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


   # Objekttypen
   organization = "ORGANIZATION"
   person = "PERSON"
   cause = "CAUSE"
   city = "CITY"
   country = "COUNTRY"
   place = "PLACE"
   date = "DATE"



