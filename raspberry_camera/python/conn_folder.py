__author__ = 'moilerat'

import os, sys

class FolderReadWrite():

    def __init__(self, folder = "~/fotonower_config"):
        self.root_folder = folder

        # Main variable
        self.counter_photo = "counter_photo"
        self.counter_upload = "counter_upload"
        self.portfolio_id = "portfolio_id"

    def aux_increment_file(self, counter_increment):

        if not os.path.exists(os.path.dirname(counter_increment)):
            os.makedirs(os.path.dirname(counter_increment))

        counter_init = 0
        if os.path.exists(counter_increment) :
            f = open(counter_increment, "r")

            counter_init_read = f.readline().rstrip()

            if counter_init_read.isdigit():
                counter_init = int(counter_init_read)
            else :
                print ("Error reading : " + str(counter_init_read) + ", expected digits !")

            f.close()

            os.remove(counter_increment)

        counter_current = counter_init + 1

        f = open(counter_increment, "w+")
        f.write(counter_current)
        f.close()



    def append_photo(self, photopath, date):

        day = date.strftime("%d%m%Y")
#        hour = date.strftime("%H")
#        minutes = date.strftime("%M")

        counter_photo_path = os.path.join(self.root_folder, day, self.counter_photo)

        self.aux_increment_file(counter_photo_path)




    def upload_one(self, photopath, date):

        day = date.strftime("%d%m%Y")
#        hour = date.strftime("%H")
#        minutes = date.strftime("%M")

        counter_upload_path = os.path.join(self.root_folder, day, self.counter_upload)

        self.aux_increment_file(counter_upload_path)



    def create_portfolio(self, portfolio_id, date):

        day = date.strftime("%d%m%Y")

        path_record_portfolio_id = os.path.join(self.root_folder, day, self.portfolio_id)

        if os.path.exists(path_record_portfolio_id) :
            print ("Error with existing portfolio !")
        else :
            f = open(path_record_portfolio_id)



    # VR needs maybe to be changed to be by name !
    def get_today_portfolio_id(self, date):

        day = date.strftime("%d%m%Y")

        path_record_portfolio_id = os.path.join(self.root_folder, day, self.portfolio_id)

        if os.path.exists(path_record_portfolio_id) :
            f = open(path_record_portfolio_id, "r")
            port_id_str = f.readline().lstrip()
            if port_id_str.isdigit() :
                return int(port_id_str)
            else :
                print ("Expected digit : " + str(port_id_str))
                return 0
        else :
            return 0

if __name__ == "__main__" :
    print("To use for test")


