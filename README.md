# ATMM
### Project Overview
This project leverages FastAPI and PostgreSQL to store, process, and serve datasets related to theoretical amino acid changes and their pathogenicity scores. The project incorporates data from dbSNP, providing a comprehensive analysis of the protein amino acid alterations associated with various diseases. The system uses over 20 pathogenicity score calculation algorithms to provide insightful analytics and aid in the research of genetic diseases.

#### API Response Format
The Protein Data API returns data in the JSON (JavaScript Object Notation) format. JSON is a widely used data interchange format that is human-readable and machine-parsable.

Here is the structure of the JSON response:
````
{
  "1": {
    "A": 0.2,
    "R": 0.3,
    ...,
    "ref": "M"
  },
  "2": {
    ...
  }
  ...
}

````
#### Understanding the Structure

##### In this structure:

* The outer keys (e.g., "1", "2", etc.) represent positions of amino acids within the protein sequence.
* The values associated with these outer keys are nested dictionaries that contain information about the possible amino acids at each respective position.
* The inner dictionary keys (e.g., "A", "R", etc.) represent different types of amino acids.
* The corresponding values are numerical data related to these amino acids, such as score.
* The "ref" key in the inner dictionary represents the reference amino acid for the given position in the protein sequence.
* This structure allows you to access data related to a specific position in the protein by using the position as a key. From there, you can explore all available data related to the potential amino acids at that position.

JSON's wide usage and support across many programming languages make it an ideal format for data exchange. It enables easy consumption of the API and straightforward extraction of the relevant data about specific positions in a protein sequence.

