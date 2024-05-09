import csv
import pandas as pd
import os
from pabutools import model, rules
import re
from time import time

directory_path = "./pabulib_data/"
pbfiles = [file for file in os.listdir(directory_path) if file.endswith('.pb')]

metadataFile = 'metadata.csv'
projectsFile = 'projects.csv'

# header file definition for each files to be outputted
metadata_headers = ['election_id', 'description', 'country', 'unit', 'subunit', 'district', 'instance', 'num_projects', 'num_votes', 'budget', 'rule', 'vote_type', 'date_begin', 'date_end', 'min_sum_points', 'max_sum_points', 'language', 'edition', 'comments']
project_headers = ['election_id', 'country','unit', 'subunit', 'instance', 'project_id', 'cost', 'project_voters_count', 'votes', 'score', 'category', 'name', 'englishName', 'target', 'total_budget', 'budget_percent', 'is_mes_winner', 'is_greedy_winner', 'is_phragmen_winner', 'latitude', 'longitude']

def main():
    start_time = int(time())
    fileCount = 1
    
    # add a new variable called election id, will be used for each pb election, incremented with each pb file
    election_id = 1

    # Writing of headers for each of the output files before starting to write data
    with open(metadataFile, 'w', newline='', encoding='utf-8') as file:
        metaWriter = csv.DictWriter(file, fieldnames=metadata_headers, delimiter=';')
        metaWriter.writeheader()

    with open(projectsFile, 'w', newline='', encoding='utf-8') as f2:
        projectsWriter = csv.DictWriter(f2, fieldnames=project_headers, delimiter=';')
        projectsWriter.writeheader()

    num_projects = 1
    for pbfile in pbfiles:

        # to be populated with data relating to metadata, voting and projects data
        # we should reset these values with each file, because, these if not, we would exponentially write them with each loop
        metadata_arrays = []
        project_arrays = []
        
        pbfilePath = os.path.join(directory_path, pbfile)
        print(pbfilePath)
        print("file count is: ", fileCount)
        with open(pbfilePath, 'r', newline='', encoding="utf-8") as dotpbfile:
            meta = {}
            section = ""
            header = []
            
            # pb file are delimited by ;, since voting data can be accumulated in multiple manners!
            reader = csv.reader(dotpbfile, delimiter=';')

            # getting electiondata using pabutools model library
            election_data = model.Election().read_from_files(pbfilePath)
            election_budget = election_data.budget

            # use RE to match pattern of the results of the selected candidates
            pattern = r"c\(([\w\d/.]+)\)"

            # getting results using mes
            mes_winners_object = rules.equal_shares(election_data, completion='add1_utilitarian')
            mes_winners_stringified = str(mes_winners_object)
            mes_matches = re.findall(pattern, mes_winners_stringified)
            mes_winners_id = [match for match in mes_matches]

            # getting results using greedy aggregation
            greedy_winners_object = rules.utilitarian_greedy(election_data)
            greedy_winners_stringified = str(greedy_winners_object)
            greedy_matches = re.findall(pattern, greedy_winners_stringified)
            greedy_winners_id = [match for match in greedy_matches]

            # getting results using phragmen aggregation
            phragmen_winners_object = rules.phragmen(election_data)
            phragmen_winners_stringified = str(phragmen_winners_object)
            phragmen_matches = re.findall(pattern, phragmen_winners_stringified)
            phragmen_winners_id = [match for match in phragmen_matches]

            # Reading each row from the pb file
            for row in reader:
                if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
                    section = str(row[0]).strip().lower()
                    header = next(reader) # reads the next item in the iterator; i.e. the name of attributes in case of projects and votes

                # the rest of the elif snippet has already navigated to the next line, since the first if condition checks for META, PROJECTS or VOTES and sets section and header values
                # matching for meta section
                elif section == "meta":
                    # add each key value pair under META as a dictionary object
                    meta[row[0]] = row[1].strip()
                
                # matching for projects section
                elif section == "projects":
                    num_projects += 1
                    # projects[row[0]] = {}
                    singleProjectData = {}

                    # setting the country, year, unit and subunit info from meta section which has already been initialized
                    singleProjectData['election_id'] = election_id
                    singleProjectData['country'] = meta.get('country','')
                    singleProjectData['instance'] = meta.get('instance','')
                    singleProjectData['unit'] = meta.get('unit','')
                    singleProjectData['subunit'] = meta.get('subunit','')
                        
                    for it, key in enumerate(header):
                        singleProjectData[key] = row[it].strip()

                    # translate the project description from Polish to English
                    # singleProjectData['englishName'] = translate_text(singleProjectData['name'])
                    
                    # added a new field total budget of the PB election
                    singleProjectData['total_budget'] = election_budget
                    singleProjectData['project_voters_count'] = meta.get('num_votes', 0)

                    # added a new column, budget_percentage
                    budget_pct = float(int(singleProjectData['cost']) / election_budget) * 100
                    singleProjectData['budget_percent'] = round(budget_pct, 3) # rounding off upto 3 decimal places


                    # added a new field for identifying if the project is a winner by MES aggregation method
                    if(singleProjectData['project_id'] in mes_winners_id):
                        singleProjectData['is_mes_winner'] = True
                    else:
                        singleProjectData['is_mes_winner'] = False

                    # added a new field for identifying if the project is a winner by greedy aggregation method
                    if(singleProjectData['project_id'] in greedy_winners_id):
                        singleProjectData['is_greedy_winner'] = True
                    else:
                        singleProjectData['is_greedy_winner'] = False

                    # added a new field for identifying if the project is a winner by phragmen method
                    if(singleProjectData['project_id'] in phragmen_winners_id):
                        singleProjectData['is_phragmen_winner'] = True
                    else:
                        singleProjectData['is_phragmen_winner'] = False

                    project_arrays.append(singleProjectData)

                # matching for votes data
                elif section == "votes":
                    continue
                
            # add election_id to the metadata file too; so that it can be used to identify
            meta['election_id'] = election_id

            # we append metadata_arrays at the end because there is just one entry for metadata per PB file; we could do it at either the start of projects 
            # section or votes section
            metadata_arrays.append(meta)

        
        # append metadata to the metadata.csv file
        with open(metadataFile, 'a', newline='', encoding='utf-8') as file:
            metaWriter = csv.DictWriter(file, fieldnames=metadata_headers, delimiter=';')
            metaWriter.writerows([{ k: metadata.get(k, '') for k in metadata_headers } for metadata in metadata_arrays ])

        
        # append projects info to the projects.csv file
        with open(projectsFile, 'a', newline='', encoding='utf-8') as f2:
            projectsWriter = csv.DictWriter(f2, fieldnames=project_headers, delimiter=';')
            projectsWriter.writerows([{ k: project.get(k, '') for k in project_headers } for project in project_arrays ]) 

        fileCount = fileCount + 1
        election_id = election_id + 1
        print("Total projects are: ", num_projects)


    # section for translating text from polish to english
    # projects_df = pd.read_csv('./projects.csv', delimiter=';')
    # projects_df['englishName'] = projects_df.apply(translate_text, axis=1)
    # projects_df.to_csv('projects.csv', index=False, sep=';')

    end_time = int(time())
    time_elapsed = end_time - start_time
    print("Time elapsed: ", time_elapsed)
    

if __name__ == "__main__":
    main()