# ---------------------------------------------------------------------------------------
# downloads google images using google-images-download python script
# Because google-images-download can download up to 100 images per call
# we used the time_range filter to download 100 per day
# Kindly specify a start_date and end_date in order to obtain 100 images per day
# The pacakge was downloaded to /home/dan/source/taboola/3rd_party/google-images-download/google_images_download.py
# but in order to fix a bug, i copied a copy to this directory and updated the python file
# Prerequisites:
# 1. Make sure the file google_images_download.py exists in the same directory
# 2. The file google_images_download.py can be found here - google_images_download.py (There was a bug so please use the version here)
# 3. sudo apt-get install python3-urllib3 # for python 3
#    or
#    pip3 install urllib3 # for python 3
#
#    Usage example:
#    Usage  : python download_google_images_in_time_range.py search_keywords requested_start_date(mm/dd/yyyy) num_of_days download_limit_per_day(max 100)  output_directory  split_by_date_flag
#    Example: python download_google_images_in_time_range_main.py dog 01/25/2018 70 /home/dan/source/taboola/3rd_party/google-images-download/google_images_download/downloads/ 0
#             This downloads dog images created 01/25/2018 and the next 70 days, 98 images per day, to the directory /home/dan/source/taboola/3rd_party/google-images-download/google_images_download/downloads/dog/
# Author: Dan
# Last updated: 2018-05-06
# ---------------------------------------------------------------------------------------


import google_images_download
import sys
import datetime
import threading

def download_images_per_date(search_keywords,requested_date,download_limit,output_directory,split_by_date_flag):
    print('search_keywords            [', search_keywords, ']')
    print('requested_date ,mm/dd/yyyy [', requested_date.strftime('%Y_%m_%d'), ']')
    print('download_limit             [', download_limit, ']')
    print('search_keywords            [', search_keywords, ']')
    print('output_directory           [', output_directory, ']')
    print('split_by_date_flag         [', split_by_date_flag, ']')

    requested_date_string_mmddyyyy=requested_date.strftime('%m/%d/%Y')
    requseted_date_subdirectory=requested_date.strftime('%Y_%m_%d')

    output_directory_arg=output_directory
    if(split_by_date_flag):
        output_directory_arg=output_directory+requseted_date_subdirectory+'/'

    print('output_directory_arg           [', output_directory_arg, ']')

    response = google_images_download.googleimagesdownload()

    arguments = {"keywords": search_keywords,
                 "limit": download_limit,
                 "print_urls": True,
                 'time_range': str({"time_min": requested_date_string_mmddyyyy, "time_max": requested_date_string_mmddyyyy}),
                 "output_directory": output_directory_arg}

    print('Before download', arguments)
    response.download(arguments)  # passing the arguments to the function
    print('Finished download. Requested date [', requseted_date_subdirectory, ']')

    #
    # # Here is an example of the expected format for the arguments
    # # arguments = {"keywords": "dog",
    # #              "limit": 3,
    # #              "print_urls": True,
    # #              'time_range': str({"time_min":"04/05/2017","time_max":"04/05/2017"}),
    # #              "output_directory" : '/home/dan/source/taboola/3rd_party/google-images-download/google_images_download/downloads/'}  # creating list of arguments




def download_images_date_range(search_keywords,start_date,end_date,download_limit,output_directory,split_by_date_flag):
    current_date = start_date
    delta = datetime.timedelta(days=1)
    while current_date <= end_date:
        print ('Before - starting the download thread ',current_date.strftime("%Y-%m-%d"))
        args_tuple=(search_keywords,current_date,download_limit,output_directory,split_by_date_flag)
        download_thread = threading.Thread(target=download_images_per_date, args=args_tuple)
        download_thread.start()
        print('After - download thread started ',current_date.strftime("%Y-%m-%d"))
        # download_images_per_date(search_keywords,current_date,download_limit,output_directory,split_by_date_flag)
        current_date+=delta



def main():

    # getting inputs in the command line
    # search_keywords, requested_date (mm/dd/yyyy), download_limit, output_directory, split_by_date_flag
    num_of_arguments=len(sys.argv)
    if(num_of_arguments==7):
        search_keywords=sys.argv[1]
        requested_start_date_string = sys.argv[2]
        num_of_days = int(sys.argv[3])
        download_limit = int(sys.argv[4])
        output_directory = sys.argv[5]
        split_by_date_flag = int(sys.argv[6])

        print('search_keywords                         [',search_keywords,']')
        print('requested_start_date_string ,mm/dd/yyyy [', requested_start_date_string, ']')
        print('num_of_days                             [', str(num_of_days), ']')
        print('download_limit                          [', download_limit, ']')
        print('search_keywords                         [', search_keywords, ']')
        print('output_directory                        [', output_directory, ']')
        print('split_by_date_flag                      [', split_by_date_flag, ']')
    else:
        print('Usage  : python download_google_images_in_time_range_main.py search_keywords requested_start_date(mm/dd/yyyy) num_of_days download_limit_per_day(max 100)  output_directory  split_by_date_flag')
        print('Example: python download_google_images_in_time_range_main.py dog 01/25/2018 70 /home/dan/source/taboola/3rd_party/google-images-download/google_images_download/downloads/ 0')
        print('         This downloads dog images created 01/25/2018 and the next 70 days, 98 images per day, to the directory /home/dan/source/taboola/3rd_party/google-images-download/google_images_download/downloads/dog/ ')
        exit(-1)

    requested_start_date = datetime.datetime.strptime(requested_start_date_string, '%m/%d/%Y')
    requested_end_date = requested_start_date+ datetime.timedelta(days=num_of_days)

    download_images_date_range(search_keywords,
                               requested_start_date,
                               requested_end_date,
                               download_limit,
                               output_directory,
                               split_by_date_flag)


if __name__ == '__main__':
    main()

