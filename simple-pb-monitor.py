#!/usr/bin/python3
import requests
import time
import sys
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="A simple scraper for Pastebin written in Python")
    parser.add_argument("--path", "-p", default=".", 
                        help="base path to store pastes that match keywords")
    parser.add_argument("--keywords", "-k", default="keywords.txt", 
                        help="path to file with keywords to look for")
    parser.add_argument("--check-ip", "-ip", action="store_true", 
                        help="check if current ip address is whitelisted with Pastebin")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="increase verbosity")
    args = parser.parse_args()
    return args
    

# Check for command line parameters for the keywords file and output directory
# Start with defaults of ./keywords.txt and .

# Start with defaults
#keyword_file = 'keywords.txt'
#output_path = '.'
#check_ip = True

# keywords file as the first argument after the python file
#if len(sys.argv) > 1 :
    #keyword_file = (sys.argv)[1]

# output directory as the second parameter after the python file
#if len(sys.argv) > 2 :
    #output_path = (sys.argv)[2]

# Turn on the check for non-authed IP
#if len(sys.argv) > 3 :
    #if 'True' in (sys.argv)[3] :
        #check_ip = True

def main():
    args = parse_args()
    
    # Load the keywords
    try:
        with open(args.keywords) as f:
            keywords = f.read().splitlines()
    except:
        print("[!!] Unable to load keyword file, exiting...")
        sys.exit(-1)
    
    if args.verbose:
        print ("[*] Keywords: ", keywords)

    check_index = 0
    check_list = []

    while True :
        if args.verbose:
            print ("[*] Starting a loop")

        # get the jsons from the scraping api
        r = requests.get("https://scrape.pastebin.com/api_scraping.php?limit=100")

        # if it was successful parse
        if r.status_code == 200 :
            # Added a debug statement if the API is not authed, it has to be enabled through the params though to stop
            # pastes containing the text causing false positives (especially as the response code is 200 regardless)
            if args.check_ip :
                if ("[!!] DOES NOT HAVE ACCESS") in (str)(r.content) :
                    print ("[!!]" + r.content)
                    exit (-1)            

            # get json from the response
            parsed_json = r.json()

            # loop through the entries
            for individual in parsed_json :
                # Now get the actual pastes if it is not in the last 1000 check_list
                if individual['key'] not in check_list :
                    p = requests.get (individual['scrape_url'])
                    if p.status_code == 200 :
                        text = p.text
                        # loop through the keywords to see if they are in the post
                        for word in keywords :
                            if word.lower() in text.lower() :
                                print ('[*] Matched keyword \'{}\' and will save {}'.format(word, individual['key']))

                                # Check whether the directory with the name of the keyword exists and create it if not
                                if not os.path.isdir (args.path+'/'+word) :
                                    # Create the directory
                                    os.mkdir (args.path+'/'+word)

                                # Save to current dir using the key as the filename
                                file_object = open(args.path+'/'+word+'/'+individual['key'], 'w', encoding="utf8")
                                file_object.write(text)
                                file_object.close()

                            # Removed the break because we do want to save multiple times if multiple keywords are
                            # matched because we now have a directory per key word '''

                        # Add to the checklist of the last 1000 so we don't fetch unnecessarily
                        if check_index == 999:
                            print("[*] Reseting the checklist counter")
                            check_index = 0
                        # at the key to the last 1000 check_list and increment the counter
                        check_list.insert(check_index,individual['key'])
                        check_index = check_index + 1
                        
                    else :
                        print ("[!!] There was an error calling the url") 
                        
                elif args.verbose :
                    print ("[*] Skipping {}, already processed".format(individual['key']))



        # wait a minute
        if args.verbose:
            print ("[*] Sleeping a minute")
        time.sleep(60)


if __name__ == "__main__":
    main()
