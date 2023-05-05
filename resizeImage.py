import os
import sys
import PIL.Image as Image

size = 40, 40

files = ['img.png']
for infile in files: #sys.argv[1:]:
    outfile = os.path.splitext(infile)[0]+ '_small.png'
    if infile != outfile:
        try:
            im = Image.open(infile)
            im.thumbnail(size, Image.Resampling.LANCZOS)
            im.save(outfile, "PNG")
        except IOError:
            print(f'cannot create thumbnail for "{infile}"')