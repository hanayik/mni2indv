import csv
import sys
import os
from subprocess import call
from subprocess import check_output
import shutil

def getinputs():
    inputs = sys.argv
    inputs.pop(0)  # remove first arg (name of file)
    refimg = ''
    inimg = ''
    anatfile = ''
    for i, v in enumerate(inputs):
        if v == '-refimg':
            refimg = inputs[i+1]
        if v == '-inimg':
            inimg = inputs[i+1]
        if v == '-anatfile':
            anatfile = inputs[i + 1]
    return anatfile, refimg, inimg

def fileparts(fnm):
    import os
    e_ = ''
    e2_ = ''
    nm_ = ''
    pth_ = ''
    pth_ = os.path.dirname(fnm)
    nm_, e_ = os.path.splitext(os.path.basename(fnm))
    if ".nii" in nm_:
        nm_, e2_ = os.path.splitext(nm_)
    ext_ = e2_+e_
    return pth_, nm_, ext_


def getfsldir():
    fsldir = os.getenv("FSLDIR")
    return fsldir


def getbet():
    fsldir = getfsldir()
    betpth = os.path.join(fsldir, "bin", "bet")
    return betpth


def getrfov():
    fsldir = getfsldir()
    rfovpth = os.path.join(fsldir, "bin", "robustfov")
    return rfovpth


def getimg2imgcoord():
    fsldir = getfsldir()
    img2imgcoordpth = os.path.join(fsldir, "bin", "img2imgcoord")
    return img2imgcoordpth


def getflirt():
    fsldir = getfsldir()
    flirtpth = os.path.join(fsldir, 'bin', 'flirt')
    return flirtpth


def doflirt(inputFile, referenceFile, dof):
    import os
    # dof = "6"  # rigid body only
    ipth, inm, ie = fileparts(inputFile)
    rpth, rnm, re = fileparts(referenceFile)
    outmat = os.path.join(ipth, "r" + inm + ".mat")
    outimg = os.path.join(ipth, "r" + inm + ie)
    cmd = [
        flirt,
        "-dof",
        dof,
        "-in",
        inputFile,
        "-ref",
        referenceFile,
        #"-out",
        #outimg,
        "-omat",
        outmat
    ]
    print(cmd)
    #if os.path.exists(outmat):
     #   return outmat, outimg
    call(cmd)
    return outmat, outimg


def deleteTempFiles(files):
    for f in files:
        print("deleting file: {}".format(f))
        os.remove(f)


def doBet(fnam, f):
    p, n, e = fileparts(fnam)
    outFile = os.path.join(p, "b" + n + e)  # "o" for reoriented file
    cmd = [
        bet,
        fnam,
        outFile,
        "-f",
        f,
        "-R",
    ]
    print(cmd)
    #if os.path.exists(outFile):
     #   return outFile
    call(cmd)
    return outFile


def addToDeleteList(dlist, fname):
    dlist.append(fname)
    return dlist


def cropZ(fname):
    # crop in z dimension to improve bet results
    pth, nm, e = fileparts(fname)
    outname = os.path.join(pth, "f" + nm + e)
    outmname = os.path.join(pth, "f" + nm + ".mat")
    cmd = [
        rfov,
        "-i",
        fname,
        "-r",
        outname,
        "-m",
        outmname
    ]
    print(cmd)
    call(cmd)
    return outname, outmname


def moveFile(infile, newfolder):
    pth, nm, e = fileparts(infile)
    shutil.move(infile, os.path.join(newfolder, nm + e))


def img2imgcoord(srcimg, destimg, xfm, coords):
    # echo -5 -36 -11 | img2imgcoord -src mni152.nii -dest T1_NS003_POLARz.nii -xfm outmat.mat -mm -
    newcoords = []
    for point in coords:
        xmm = point[1]
        ymm = point[2]
        zmm = point[3]
        pth, nm, e = fileparts(destimg)
        outname = os.path.join(pth, nm + ".anat")
        cmd = [
            "echo",
            xmm,
            ymm,
            zmm,
            "|",
            img2img,
            "-src",
            srcimg,
            "-dest",
            destimg,
            "-xfm",
            xfm,
            "-mm"
        ]
        res = check_output(" ".join(cmd), shell=True, universal_newlines=True)
        res = res.split("\n")[1].split(" ")
        mmlist = list(filter(None, res))
        newcoords.append(list([point[0], mmlist[0], mmlist[1], mmlist[2]]))
    print(newcoords)
    with open(outname, "w") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator='\n')
        writer.writerows(newcoords)
    return outname

def parse_anat_file(file):
    coords = []
    with open(file) as f:
        for l in f:
            # print(l.strip().split("\t"))
            coords.append(l.strip().split("\t"))
    return coords

dlist = []
# get bet and flirt commands
bet = getbet()  # get path to bet command
flirt = getflirt()  # get path to flirt command
rfov = getrfov()  # used if cropping is desired
img2img = getimg2imgcoord()  # map points between two images (given a transform matrix exists that relates the two)

# get inputs to makeLesion.py
anatfile, refimg, inimg = getinputs()  # parse inputs

coords = parse_anat_file(anatfile)  # anat file is tab delimited, so parse it into a list

brain_refimg = doBet(refimg, "0.5")  # brain extract the individual's image (since MNI is brain extracted)

mni2indmat, mni2ind = doflirt(inimg, brain_refimg, "9")  # linearly register MNI into individual space

dlist = addToDeleteList(dlist, mni2indmat)  # will delete some temp files

img2imgcoord(inimg, refimg, mni2indmat, coords)  # get point-to-point mapping for all landmarks in anat file

dlist = addToDeleteList(dlist, brain_refimg)  # will delete some temp files

deleteTempFiles(dlist)  # now actually delete temp files

