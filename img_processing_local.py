from PIL import Image
import os

def optimize(img, path, infile):
    base_size = 512
    if img.size[0] > img.size[1]:
        size_per = base_size / (float(img.size[0]))
        new_size = int((float(img.size[1])) * float(size_per))
        new_img = img.resize((base_size, new_size), Image.ANTIALIAS)
    else:
        size_per = base_size / (float(img.size[1]))
        new_size = int((float(img.size[0])) * float(size_per))
        new_img = img.resize((new_size, base_size), Image.ANTIALIAS)
    new_img.save(os.path.join(path,infile))

def get_path():
    path = input("Enter path: ")
    new_path = os.path.join(path, 'optimized')
    try:
        os.mkdir(new_path)
    except FileExistsError:
        pass
    return (path,new_path)

def main():
    path = get_path()
    for infile in os.listdir(path[0]):
        try:
            with Image.open(os.path.join(path[0], infile)) as img:
                optimize(img, path[1], infile)
        except IOError:
            pass
