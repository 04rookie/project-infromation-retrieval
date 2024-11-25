import wikipedia
import json
from time import sleep
import re

titles = set()
# Defining topics
topics = ["Health", "Environment", "Technology", "Economy", "Entertainment", "Sports", "Politics", "Education", "Travel", "Food"]
def scrape():
    try:
        # Main data structure that will hold all the data
        main_result = {}

        # Counters to show progress while scraping
        topic_count, search_result_count = 0, 0

        # Looping through each topic
        for topic in topics:
            print("Topic: ", topic, "Topic Count: ", topic_count)
            # initialising a list for each topic
            main_result[topic] = []
            # searching for 700 results for each topic (Although we get roughly 500 results per topic)
            search_results = wikipedia.search(topic, 700)
            # Going through each search result
            for search_result in search_results:
                print("Search Result Count: ", search_result_count, "Topic: ", topic)
                # Sleeping for 0.2 seconds to avoid getting blocked by wikipedia, alternatively we can use await.
                sleep(.2)
                try:
                    content = wikipedia.page(search_result, auto_suggest=False)
                    structured_content = {
                        "title": content.title,
                        "summary": content.summary,
                        "revision_id": content.revision_id,
                        "url": content.url,
                        "topic": topic
                    }
                    main_result[topic].append(structured_content)
                except:
                    # If we are not able to get any content for a particular result, we just skip it
                    search_result_count += 1
                    continue
                search_result_count += 1
            topic_count += 1
            search_result_count = 0
    except:
        print("Error")

    # Saving the data in a json file
    with open("initial_search_results.json", "w") as file_pointer:
        json.dump(main_result, file_pointer)
        file_pointer.close()     
# scrape()


# Loading the data from the json file

# Counters to find how many addtional documents are required for each topic
additional_document_requirement = {}
def calculate_additional_scraping():
    result = None
    for topic in topics:
        additional_document_requirement[topic] = 0

    # Loading the data and finding how many additional documents are required for each topic
    with open("initial_search_results.json", "r") as file_pointer:
        result = json.load(file_pointer)
        print("---------------------------------------------------")
        for topic, documents in result.items():
            # less_than_200 tells us how many documents are less than 200 words
            # sum is used to calculate average before initial preprocessing
            less_than_200, sum = 0, 0
            for document in documents:
                sum = sum + len(document["summary"])
                if len(document["summary"]) < 200:
                    less_than_200 += 1
                titles.add(document["title"])  
            print("Less than 200 in: ", topic, ": ",less_than_200)
            print("Sum of length in", topic, ": ", sum)
            print("Average in ", topic, ": ", sum/len(documents))
            # how many addtional documents are required for each topic
            additional_document_requirement[topic] = 700 - len(result[topic]) + less_than_200
        file_pointer.close()
    print(additional_document_requirement)

# calculate_additional_scraping()


# Scraping additional documents
def scrap_addtional_documents():
    result = {}
    # initalising a list for each topic
    for topic in topics:
        result[topic] = []
    try: 
        for topic in topics:
            search_results = wikipedia.search(topic, 2)
            # we need to scrape these many addtional documents for each topic
            scrap_count = additional_document_requirement[topic]
            content = None
            content_links = None
            try:
                content = wikipedia.page(search_results[0])
                content_links = content.links
            except wikipedia.DisambiguationError as e:
                # many pages throw disambiguation error, we just move on to next option
                content = wikipedia.page(e.options[0], auto_suggest=False)
                content_links = content.links
            except:
                #if any addtional error is caught we consider the second search result 
                # (not the best solution, could be improved later)
                content = wikipedia.page(search_results[1], auto_suggest=False)
                content_links = content.links
            while scrap_count > 0:
                try:
                    for link in content_links:
                        sleep(.02)
                        print("Topic: ", topic, "scraping count: ", scrap_count)
                        try:
                            if(scrap_count == 0):
                                break
                            # if we have already scraped this link, we move on
                            if link in titles:
                                continue
                            content = wikipedia.page(link, auto_suggest=False)
                            structured_content = {
                                "title": content.title,
                                "summary": content.summary,
                                "revision_id": content.revision_id,
                                "url": content.url,
                                "topic": topic
                            }
                            result[topic].append(structured_content)
                            scrap_count -= 1
                            titles.add(link)
                        except:
                            continue
                        # if we have exhausted content_links of current page, move on to last page's content list
                        if(scrap_count !=0):
                            content_links = content.links
                except:
                    continue

        # update the file with addtional scraped data 
        with open("initial_search_results.json", "r") as file_pointer:
            initial_result = json.load(file_pointer)
            for topic in topics:
                initial_result[topic].extend(result[topic])
            with open("initial_search_results.json", "w") as file_pointer_dump:
                json.dump(initial_result, file_pointer_dump)
                file_pointer_dump.close()
            file_pointer.close()

    except:
        # if any runtime error is caught while scraping, we just dump the progress made so far
        with open("initial_search_results.json", "r") as file_pointer:
            initial_result = json.load(file_pointer)
            for topic in topics:
                initial_result[topic].extend(result[topic])
            with open("initial_search_results.json", "w") as file_pointer_dump:
                json.dump(initial_result, file_pointer_dump)
                file_pointer_dump.close()
            file_pointer.close()

# scrap_addtional_documents()
# calculate_additional_scraping()

# to check if the documents are meeting requirements
def analytics(filename, limit = 250):
    result = None
    # counter for duplicates
    duplicates = 0
    # counter for documents that are below the limit
    below_limit = 0
    # set for titles to check for duplicates
    title_set = set()
    # counter for hex values
    hex_values = 0
    hex_title = 0
    # counter for total number of documents
    doc_len = 0
    with open(filename, "r") as file_pointer:
        result = json.load(file_pointer)
        for topic, documents in result.items():
            print(topic, " length: ", len(documents))
            doc_len += len(documents)
            for document in documents:
                # Document already scraped
                if document["title"] in title_set:
                    duplicates += 1
                else:
                    # Add in set
                    title_set.add(document["title"])
                if len(document["summary"]) < limit:
                    below_limit += 1
                # check for hex values, if exists increase the counter
                if(len(re.findall(r'[^a-zA-Z0-9 ]', document["summary"])) > 0):
                    hex_values += 1
                
        file_pointer.close()
    print("Duplicates: ", duplicates)
    print("Below limit: ", below_limit)
    print("Hex values: ", hex_values)
    print("Hex percentage: ", (hex_values/doc_len) * 100)
    print("Document length: ", doc_len)

# analytics("initial_search_results.json", 200)

def preprocessing():
    result = None
    titles_set = set()
    with open("initial_search_results.json", "r") as file_pointer:
        result = json.load(file_pointer)
        for topic, documents in result.items():
            # removing punctuations and special characters
            for document in documents:
                processed_summary = ""
                for c in document["summary"]:
                    if c.isalnum() or c == " ":
                        processed_summary += c
                # removing hex characters
                document["summary"] = re.sub(r'[^a-zA-Z0-9 ]', '', processed_summary)
            new_collection = []
            # removing documents that are less than 200 words and duplicates
            for document in documents:
                if len(document["summary"]) > 199 and document["title"] not in titles_set:
                    titles_set.add(document["title"])
                    new_collection.append(document)
            result[topic] = new_collection
        file_pointer.close()
    # generating new final result
    with open("search_results.json", "w") as file_pointer:
        json.dump(result, file_pointer)
        file_pointer.close()

# preprocessing()
# analyse again
analytics("search_results.json", 200)
# analytics("initial_search_results.json", 200)


