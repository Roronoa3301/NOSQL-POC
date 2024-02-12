import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    temperature=0.0001,
    model_name="gpt-3.5-turbo",
    verbose=True,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

table_schema = """
{
  "_id": "string",
  "address": {
    "building": "string",
    "coord": ["number", "number"],
    "street": "string",
    "zipcode": "string",
  },
  "borough": "string",
  "cuisine": "string"
  "grades": [
    {
      "date": "date",
      "grade": "string",
      "score": "number"
    }
  ],
  "name": "string",
  "restaurant_id": "string"
}
"""

schema_description = """

Here is the description to determine what each key represents
  1. **_id**:
    - Description: Unique identifier for the document.
  2. **address**:
    - Description: Details about the restaurant's address.
  3. **building**:
    - Description: The building number of the restaurant's address.
  4. **coord**:
    - Description: Array containing longitude and latitude coordinates of the restaurant's location.
  5. **street**:
    - Description: The street name of the restaurant's address.
  6. **zipcode**:
    - Description: The ZIP code of the restaurant's address.
  7. **borough**:
    - Description: The borough where the restaurant is located.
  8. **cuisine**:
    - Description: The type of cuisine served at the restaurant.
  9. **grades**:
    - Description: Array containing past grades received by the restaurant.
  10. **date**:
    - Description: The date the grade was issued.
  11. **grade**:
    - Description: The grade received by the restaurant.
  12. **score**:
    - Description: The score associated with the grade.
  13. **name**:
    - Description: The name of the restaurant.
  14. **restaurant_id**:
    - Description: Unique identifier for the restaurant.
"""


PROMPT_MONGO_QUERY = """
Create a MongoDB raw aggregation query for the following user question: 
###{user_message}###

This is table schema : "{table_schema}"
This is schema  description : ${schema_description}$

You will use the table schema and schema description to create the MongoDB raw aggregation query based on the user question.

Do not use $match

Just return the [] of aggregration pipeline.
The following is the format instructions. 
***{format_instructions}***
"""

input_variables = [
    "user_message",
    "schema_description",
    "table_schema"
]


def get_mongo_query(user_input):
    try:
        with get_openai_callback() as cb:
            mongo_response_schema = [ResponseSchema(
                name="query", description="MongoDB Raw Query", type='string'
            )]

            output_parser = StructuredOutputParser.from_response_schemas(
                mongo_response_schema)
            format_instructions = output_parser.get_format_instructions()

            _prompt = ChatPromptTemplate.from_template(PROMPT_MONGO_QUERY)
            chain = _prompt | llm | output_parser
            data = chain.invoke({
                "user_message": user_input,
                "schema_description": schema_description,
                "table_schema": table_schema,
                "format_instructions": format_instructions
            })
            final_result = data['query']
        return final_result
    except Exception as e:
        return str(e)
