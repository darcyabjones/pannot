# pannot

Darcy Jones - <da8jones@students.latrobe.edu.au>

pannot runs a series of analyses on a set a protein sequences (a predicted proteome for example) and combines them into a series of GFF3, and query friendly tsv files.

Really this is a makefile with a bunch of python scripts and is only intended for in-house work.
But if you're interested, please feel free to contact me.


## Wishlist

- [x] interproscan
- [x] deltablast against swissprot
- [x] deltablast against pdb
- [ ] deltablast against refseq
- [ ] rpsblast against Cdd
- [x] signalp
- [x] tmhmm
- [x] targetp
- [ ] secretomep
- [x] transposonPSI
- [ ] [PredictProtiein](https://www.predictprotein.org/) secondary structure prediction
- [x] [dbCAN](http://csbl.bmb.uga.edu/dbCAN/index.php)

Eventually I'd like to get this running in a [docker](https://www.docker.com/) container for portability.

## Installation

prerequisite software:

- [blast+](ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)
- [TransposonPSI](http://transposonpsi.sourceforge.net/)
- [legacy blast](ftp://ftp.ncbi.nlm.nih.gov/blast/executables/release/LATEST/) (Required for TransposonPSI)
- [interproscan](https://github.com/ebi-pf-team/interproscan)
- [signalp](http://www.cbs.dtu.dk/cgi-bin/nph-sw_request?signalp)
- [tmhmm](http://www.cbs.dtu.dk/cgi-bin/nph-sw_request?tmhmm)
- [targetp](http://www.cbs.dtu.dk/cgi-bin/nph-sw_request?targetp)
- [chlorop](http://www.cbs.dtu.dk/cgi-bin/nph-sw_request?chlorop) (dependency of targetp)
- [secretomep](http://www.cbs.dtu.dk/services/SecretomeP/)
- [ProP](http://www.cbs.dtu.dk/cgi-bin/nph-sw_request?prop) (dependency of secretomep)
- [PSORT II](http://psort.hgc.jp/) (dependency of secretomep). Hard to get, waiting for reply from <knakai@ims.u-tokyo.ac.jp> .
- python 2.7+ or python 3.4+ (untested with other versions)

Assumes that you have these blast databases available on the `BLASTDB` path:

- cdd_delta
- taxdb
- swissprot
- pbd

You can easily download these with the following commands from your desired directory:

```bash
$ # wget -t0 --timestamping --no-remove-listing "ftp://ftp.ncbi.nih.gov/pub/mmdb/cdd/little_endian/*" && tar zxf Cdd_LE.tar.gz
$ update_blastdb.pl --decompress taxdb cdd_delta pdbaa swissprot
```


download extra databases:

```bash
wget http://csbl.bmb.uga.edu/dbCAN/download/FamInfo.txt -O data/FamInfo.txt
wget http://csbl.bmb.uga.edu/dbCAN/download/CAZyDB-ec-info.txt -O data/CAZyDB-ec-info.txt
wget ftp://ftp.pantherdb.org//hmm_classifications/current_release/PANTHER10.0_HMM_classifications -O data/PANTHER10.0_HMM_classifications

wget http://www.geneontology.org/external2go/pfam2go -O data/pfam2go
wget http://www.geneontology.org/external2go/smart2go -O data/smart2go
wget http://www.geneontology.org/external2go/interpro2go -O data/interpro2go
wget http://geneontology.org/external2go/prosite2go -O data/prosite2go
wget http://geneontology.org/external2go/prints2go -O data/prints2go
wget http://geneontology.org/external2go/prodom2go -O data/prodom2go
wget http://supfam.cs.bris.ac.uk/SUPERFAMILY/Domain2GO/Domain2GO_supported_only_by_all.txt -O data/domain2go
```
