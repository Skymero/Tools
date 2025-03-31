# Tapa Tool Architecture

This document provides detailed diagrams of the Tapa Tool's architecture and workflow using PlantUML.

## Overview

The Tapa Tool is designed to:
1. Extract parts requirements from specification documents
2. Search for matching parts on Mouser.com
3. Verify TAA compliance of found parts
4. Output TAA compliant parts to structured formats

## Class Structure

```plantuml
@startuml

' Class definitions
class RequirementsExtractor {
  -file_path: str
  +__init__(file_path: str)
  +extract(): Dict[str, Dict[str, Any]]
  -_extract_from_text(): Dict[str, Dict[str, Any]]
  -_extract_from_csv(): Dict[str, Dict[str, Any]]
  -_extract_from_json(): Dict[str, Dict[str, Any]]
}

class MouserScraper {
  -requirements: Dict[str, Any]
  -headers: Dict[str, str]
  -session: requests.Session
  +__init__(requirements: Dict[str, Any])
  +build_search_query(): str
  +search(): List[Dict[str, str]]
}

class TAAComplianceChecker {
  -headers: Dict[str, str]
  -session: requests.Session
  +__init__()
  +check_compliance(part_url: str): Tuple[bool, str]
}

' Helper functions
class "Functions" as Functions << (F,#FFCC00) >> {
  +print_parts_table(parts, title, include_compliance=False)
  +save_parts_to_csv(parts, filename)
  +main()
}

' Relationships
Functions --> RequirementsExtractor: creates
Functions --> MouserScraper: creates for each requirement
Functions --> TAAComplianceChecker: creates if --check-taa
RequirementsExtractor ..> "returns" Dictionary
MouserScraper ..> "returns" List
TAAComplianceChecker ..> "returns" Tuple

@enduml
```

## Sequence Diagram

```plantuml
@startuml

actor User
participant "main()" as Main
participant "RequirementsExtractor" as Extractor
participant "MouserScraper" as Scraper
participant "TAAComplianceChecker" as Checker
database "Mouser.com" as Mouser
database "Output Files" as Files

User -> Main: Run with arguments
activate Main

' Parse arguments
Main -> Main: Parse command-line arguments
Main -> Main: Configure logging
Main -> Main: Create output directory

' Extract requirements
Main -> Extractor: create(file_path)
activate Extractor
Main -> Extractor: extract()
Extractor -> Extractor: Determine file type
alt .txt or .md file
    Extractor -> Extractor: _extract_from_text()
else .csv file
    Extractor -> Extractor: _extract_from_csv()
else .json file
    Extractor -> Extractor: _extract_from_json()
end
Extractor --> Main: return requirements dict
deactivate Extractor

' Save requirements to JSON
Main -> Files: Save requirements to JSON
activate Files
Files --> Main: JSON file saved
deactivate Files

' Search for parts for each requirement
loop for each requirement
    Main -> Scraper: create(requirement)
    activate Scraper
    Main -> Scraper: search()
    
    ' Build search query
    Scraper -> Scraper: build_search_query()
    
    ' Search Mouser
    Scraper -> Mouser: GET search request
    activate Mouser
    Mouser --> Scraper: HTML response
    deactivate Mouser
    
    ' Parse results
    Scraper -> Scraper: Parse with BeautifulSoup
    Scraper -> Scraper: Extract part information
    
    Scraper --> Main: return parts list
    deactivate Scraper
    
    ' Add requirement ID to parts
    Main -> Main: Add requirement ID to parts
    Main -> Main: Add parts to all_parts list
end

' Print and save all parts
Main -> Main: print_parts_table(all_parts)
Main -> Files: save_parts_to_csv(all_parts)
activate Files
Files --> Main: CSV file saved
deactivate Files

' Check TAA compliance if requested
opt --check-taa argument provided
    Main -> Checker: create()
    activate Checker

    loop for each part in all_parts
        Main -> Checker: check_compliance(part['link'])
        
        ' Check compliance
        Checker -> Mouser: GET part details
        activate Mouser
        Mouser --> Checker: HTML response
        deactivate Mouser
        
        ' Parse for compliance
        Checker -> Checker: Parse with BeautifulSoup
        Checker -> Checker: Check for compliance indicators
        
        Checker --> Main: return is_compliant, evidence
        
        ' Update part info
        Main -> Main: Add compliance info to part
        Main -> Main: Add to compliant_parts if compliant
    end
    
    deactivate Checker
    
    ' Save parts with compliance info
    Main -> Files: save_parts_to_csv(all_parts with compliance)
    activate Files
    Files --> Main: CSV file saved
    deactivate Files
    
    ' Print and save compliant parts
    alt compliant_parts not empty
        Main -> Main: print_parts_table(compliant_parts)
        Main -> Files: save_parts_to_csv(compliant_parts)
        activate Files
        Files --> Main: CSV file saved
        deactivate Files
    else
        Main -> Main: Print "No TAA compliant parts found"
    end
end

Main --> User: Exit code (0 for success, 1 for failure)
deactivate Main

@enduml
```

## Flowchart

```plantuml
@startuml

!define RECTANGLE class
!define CIRCLE interface

start

:Parse command-line arguments;
:Configure logging;
:Create output directory;

:Extract requirements from input file;

:Determine file type (.txt, .csv, .json);

if (File exists?) then (yes)
  if (File type) then (text)
    :Extract from text file;
  else if (File type) then (csv)
    :Extract from CSV file;
  else if (File type) then (json)
    :Extract from JSON file;
  endif
else (no)
  :Log error;
  stop
endif

:Save requirements to JSON;

if (Requirements found?) then (yes)
  :Initialize empty all_parts list;
  
  while (More requirements?) is (yes)
    :Get next requirement;
    :Create MouserScraper;
    :Build search query;
    
    if (Query created?) then (yes)
      :Search Mouser.com;
      :Parse search results;
      
      if (Parts found?) then (yes)
        :Add requirement ID to parts;
        :Add parts to all_parts list;
      else (no)
        :Log "No parts found for requirement";
      endif
    else (no)
      :Log error;
    endif
  endwhile (no)
  
  if (all_parts not empty?) then (yes)
    :Print parts table;
    :Save all parts to CSV;
    
    if (Check TAA compliance?) then (yes)
      :Create TAAComplianceChecker;
      :Initialize empty compliant_parts list;
      
      while (More parts?) is (yes)
        :Get next part;
        :Check TAA compliance;
        :Add compliance info to part;
        
        if (Is compliant?) then (yes)
          :Add to compliant_parts list;
        endif
      endwhile (no)
      
      :Save all parts with compliance info;
      
      if (compliant_parts not empty?) then (yes)
        :Print compliant parts table;
        :Save compliant parts to CSV;
      else (no)
        :Print "No TAA compliant parts found";
      endif
    endif
    
    :Print results summary;
    :Return success (0);
  else (no)
    :Print "No parts found for any requirements";
    :Return failure (1);
  endif
else (no)
  :Print "No requirements found";
  :Return failure (1);
endif

stop

@enduml
```

## Data Flow

```plantuml
@startuml

!define RECTANGLE class
!define CIRCLE interface

RECTANGLE "Input Requirement File" as InputFile
RECTANGLE "RequirementsExtractor" as Extractor
RECTANGLE "Requirements Dictionary" as ReqDict
RECTANGLE "MouserScraper" as Scraper
RECTANGLE "Mouser.com" as Mouser
RECTANGLE "Parts List" as PartsList
RECTANGLE "TAAComplianceChecker" as Checker
RECTANGLE "Compliance Info" as Compliance
RECTANGLE "Output CSV Files" as OutputCSV
RECTANGLE "Console Output" as Console

InputFile --> Extractor : Input
Extractor --> ReqDict : Extract
ReqDict --> Scraper : For each requirement
Scraper --> Mouser : Search query
Mouser --> Scraper : Search results
Scraper --> PartsList : Parts data
PartsList --> Checker : Part URLs
Checker --> Mouser : Request part details
Mouser --> Checker : Part details page
Checker --> Compliance : Analyze
Compliance --> PartsList : Add compliance info
PartsList --> OutputCSV : Save to file
PartsList --> Console : Display

@enduml
```

## Usage Example

The Tapa Tool is run from the command line with the following syntax:

```
python tapa_tool.py --input-file <requirements_file> [--output-dir <output_directory>] [--check-taa] [--verbose]
```

### Arguments

- `--input-file`: (Required) Path to input requirements document (.txt, .csv, or .json)
- `--output-dir`: (Optional) Directory for output files (defaults to "output")
- `--check-taa`: (Optional) Enable TAA compliance checking
- `--verbose`: (Optional) Enable verbose logging

### Output Files

The tool creates the following output files:
1. `requirements.json`: Extracted requirements in JSON format
2. `all_parts.csv`: All parts found for all requirements
3. `parts_with_compliance.csv`: All parts with TAA compliance information (if --check-taa used)
4. `taa_compliant_parts.csv`: Only TAA compliant parts (if --check-taa used)

## Implementation Details

### Requirements Extraction

- Supports multiple file formats:
  - Text files (.txt, .md): Uses regex to identify requirements
  - CSV files: Identifies ID columns and maps to requirements
  - JSON files: Handles multiple JSON structures

### Mouser Scraping

- Uses the requests library to query Mouser.com
- Parses HTML with BeautifulSoup4
- Builds search queries based on available requirement fields
- Extracts part names, numbers, and links

### TAA Compliance Checking

- Retrieves detailed part pages from Mouser.com
- Searches for TAA compliance indicators in page text
- Handles multiple TAA compliant countries and phrases
- Reports evidence for compliance determinations
