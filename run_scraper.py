from resources.functions import *

if __name__ == "__main__":

    print_title()

    stop = False
    while not stop:

        tag_list = create_tag_list_from_input()
        
        if len(tag_list) == 0:
            break

        run_scraper(tag_list)

        print("Continue? [y/n]")
        continue_response = str(input())
        print()

        if continue_response != "y":
            stop = True

