import requests
import json
########################################################################################################################


def current_mtgjson_version():
    """Fetches current version number from mtgjson online and returns value as a string"""
    page = requests.get('https://mtgjson.com/json/version.json')  # json file containing version number
    mtgjson_online_version = json.loads(page.content)['version']  # parsed json containing
    return mtgjson_online_version


########################################################################################################################


def version_updater(online):
    """Depending on user input, will update the version file with the build version equal to the online version"""
    while True:  # loop used to ensure correct user input
        user_choice = input(
                    "Build Version does not equal MTGJSON version. Do you wish to record the update? (y/n): ")
        if user_choice.lower() == 'y':  # i.e. wish to update the stored build value
            with open('version_check.txt', 'r+') as f:  # open version file
                f.seek(0)  # go to start of file and write the below
                new_content = ['MTGJSON_version ' + online + '\n',
                                       'Build_version ' + online + '\n']  # updating therefore versions will match
                f.writelines(new_content)  # writes updated file content
                print('Version file now updated')
                break
        elif user_choice.lower() == 'n':  # i.e. just wanted to check if there had been an update or not
            print('Choice registered, no update will be recorded')
            break
        else:
            print('Invalid choice')  # ensures only either a 'y' or an 'n' input is received


########################################################################################################################


def main():
    """Takes version from mtgjson and compares against stored build version. if difference then prompts user"""
    with open('version_check.txt', 'r+') as f:
        build_version = f.readlines()[1].split(' ')[1].rstrip()
    if current_mtgjson_version() == build_version:
        print('Build and Online Versions Match.')
    else:
        version_updater(current_mtgjson_version())

    print('MTGJSON_version = ', current_mtgjson_version())
    print('Build_version = ', build_version)


########################################################################################################################

if __name__ == '__main__':
    main()  # Checks to see if I need to update the main database or not due to an update of mtgjson data
