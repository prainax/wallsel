import os
def image_list():
    directory = "/home/r/Downloads/wall/wallpapers-master/"

    ext = {".jpg", ".png", ".jpeg"}

    try:
        images = os.listdir(directory)

        image_list = [entry for entry in images
                      if os.path.isfile(os.path.join(directory, entry))
                      and os.path.splitext(entry)[1].lower() in ext]
        
        




        print(image_list)
    except:
        print([])


