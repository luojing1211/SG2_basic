from google_2_cataliet import SG2Image, GoogleSheetCSV, CataliteFiles
import os
import sys
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infilename', help="The input googld cvs file name.")
    parser.add_argument('-o', dest='outfilename',  default='',
                        help="The output googld cvs file name.")
    parser.add_argument('-catalite_path', dest='catapath', default='.',
                        help="The path to catalite program")
    # Parse the commonline parameters
    args = parser.parse_args()
    infile = args.infilename
    outfile = args.outfilename
    cpath = args.catapath
    c = GoogleSheetCSV(infile)
    name_field = os.path.splitext(infile)
    base_name = name_field[0]
    if outfile == '':
        outfile = base_name + '_result.txt'
    issue_img_file = base_name + '_issue_images.txt'
    cf = CataliteFiles(outfile, c, os.path.join(cpath,'Catalite'))
    result_out = ''
    issue_out =''
    for im in cf.image_clses:
        if im.good_image:
            try:
                result_out += cf.output_line(im) + '\n'
            except:
                issue_out += im.image_full_id + ' ' + str(sys.exc_info()) + '\n'
        else:
            if im.image_full_id.startswith('Image'):
                continue
            if im.image_full_id == '':
                continue
            issue_out += im.image_full_id + ' ' + im.error_msg + '\n'
    fout = open(outfile, 'w')
    iout = open(issue_img_file, 'w')
    fout.write(result_out)
    iout.write(issue_out)
    fout.close()
    iout.close()
