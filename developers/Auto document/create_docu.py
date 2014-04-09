import sys
sys.path.append(r"C:\Users\BIGKIMO\Dropbox\Work\Research\Software\Various Python Libraries\GitDoc")
import gitdoc

FILENAME = "py3d"
FOLDERPATH = r"C:\Users\BIGKIMO\Dropbox\Work\Research\Software\Various Python Libraries\Py3d"
OUTPATH = r"C:\Users\BIGKIMO\Dropbox\Work\Research\Software\Various Python Libraries\Py3d"
OUTNAME = "README"
EXCLUDETYPES = ["variable","module"]
gitdoc.Module2GitDown(FOLDERPATH,
                  filename=FILENAME,
                  outputfolder=OUTPATH,
                  outputname=OUTNAME,
                  excludetypes=EXCLUDETYPES,
                  )
