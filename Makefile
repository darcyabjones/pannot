C=$(shell pwd)
DATA=$(C)/data
PROT_FILE=I5V.codingquarry.faa
ISOLATE=$(word 1, $(subst ., ,$(PROT_FILE)))

THREADS=1
PYTHON=python
LEGACY_BLAST=/home/darcy/bin/blast-2.2.26

SPLITTER=$(PYTHON) $(C)/lib/splitter.py -i $(1) -p $(2) -n $(3)
IPS=@echo /usr/local/interproscan/5.15-54.0/interproscan-5.15-54.0/interproscan.sh -f TSV,XML,GFF3,HTML,SVG --goterms -dp --iprlookup --pathways -t p -i $(1) --output-dir $(2)
SIGNALP=signalp -f short -n $(1) -l $(2) < $(3) > $(4)
TMHMM=/usr/local/tmhmm/2.0c/bin/tmhmm < $(1) > $(2)
TARGETP=targetp -c -$(1) < $(2) > $(3)
TPSI=/usr/local/transposonpsi/08222010/transposonPSI.pl $(1) prot
DELTABLAST=deltablast -db $(1) -query $(2) -out $(3) -outfmt 11 -num_threads $(THREADS) -use_sw_tback
HMMSCAN=hmmscan --domtblout $(1) dbCAN-fam-HMMs.txt $(2) > $(3)
HMMSCAN_PARSER=hmmscan-parser.sh $(1) > $(2)

BLOCK_SIZE=1000
NSEQS = $(shell grep -c '>' $(1))
NBLOCKS = $(shell python -c "from math import ceil;print(int(ceil($(1) / $(2).)))")
RANGE = $(shell echo {1..$(call NBLOCKS, $(1), $(BLOCK_SIZE))})
SPLIT_FNAMES = $(foreach i, $(call RANGE, $(call NSEQS, $(1))), $(addsuffix -$(i).fasta, $(2)))

## Define filenames and directories

SPLIT_DIR = $(C)/split_aa
SPLIT_FILES = $(call SPLIT_FNAMES, $(DATA)/$(PROT_FILE), $(SPLIT_DIR)/$(ISOLATE))

IPS_DIR = $(C)/sub_ips
IPS_EXTS=.tsv .xml .gff3 .html .svg
IPS_FILES = $(foreach e, $(EXTS), $(foreach f, $(SPLIT_FILES), $(IPS_DIR)/$(notdir $(f))$(e)))

SIGNALP_DIR=$(C)/signalp
SIGNALP_FILES=$(foreach f, $(SPLIT_FILES), $(SIGNALP_DIR)/$(addsuffix .signalp.out, $(notdir $(f))))

TMHMM_DIR=$(C)/tmhmm
TMHMM_FILES=$(foreach f, $(SPLIT_FILES), $(TMHMM_DIR)/$(addsuffix .tmhmm.out, $(notdir $(f))))

TARGETP_DIR=$(C)/targetp
TARGETP_EXTS=.targetp.npn.out .targetp.pn.out
TARGETP_FILES=$(foreach e, $(TARGETP_EXTS), $(foreach f, $(SPLIT_FILES), $(TARGETP_DIR)/$(addsuffix $(e), $(notdir $(f)))))

TPSI_DIR=$(C)/tpsi
TPSI_EXTS=.TPSI.allHits .TPSI.topHits
TPSI_FILES=$(foreach e, $(TPSI_EXTS), $(foreach f, $(SPLIT_FILES), $(TPSI_DIR)/$(addsuffix $(e), $(notdir $(f)))))

SWISSPROT_BLAST_DIR=$(C)/swissprot_deltablast
SWISSPROT_BLAST_FILES=$(foreach f, $(SPLIT_FILES), $(SWISSPROT_BLAST_DIR)/$(addsuffix .asn, $(notdir $(f))))

PDB_BLAST_DIR=$(C)/pdb_deltablast
PDB_BLAST_FILES=$(foreach f, $(SPLIT_FILES), $(PDB_BLAST_DIR)/$(addsuffix .asn, $(notdir $(f))))

DBCAN_DIR=$(C)/dbCAN
DBCAN_EXTS=.out .out.dm .out.dm.ps
DBCAN_FILES=$(foreach e, $(DBCAN_EXTS), $(foreach f, $(SPLIT_FILES), $(DBCAN_DIR)/$(addsuffix $(e), $(notdir $(f)))))


## Commands

all: split signalp tmhmm targetp transposonpsi swissprot pdb

#interproscan

split: $(SPLIT_FILES)
interproscan: $(IPS_FILES)
signalp: $(SIGNALP_FILES)
tmhmm: $(TMHMM_FILES)
targetp: $(TARGETP_FILES)
transposonpsi: $(TPSI_FILES)
swissprot: $(SWISSPROT_BLAST_FILES)
pdb: $(PDB_BLAST_FILES)
dbcan: $(DBCAN_FILES)


$(SPLIT_FILES): $(DATA)/$(PROT_FILE)
	rm -f $(dir $@)*
	mkdir -p $(dir $@)
	$(call SPLITTER, $<, $(dir $@)$(word 1, $(subst ., ,$(notdir $<))), $(BLOCK_SIZE))
	sed -i -e 's/\*//g' $(SPLIT_FILES)

$(foreach e, $(IPS_EXTS), $(IPS_DIR)/%$(e)): $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	$(call IPS, $<, $(dir $@))

$(SIGNALP_DIR)/%.signalp.out: $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	$(call SIGNALP, $(basename $@).gff3, $(basename $@).log, $<, $@)

$(TMHMM_DIR)/%.tmhmm.out: $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	cd $(dir $@);$(call TMHMM, $<, $@)

$(TARGETP_DIR)/%.targetp.npn.out: $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	$(call TARGETP,N, $<, $@)

$(TARGETP_DIR)/%.targetp.pn.out: $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	$(call TARGETP,P, $<, $@)

$(foreach e, $(TPSI_EXTS), $(TPSI_DIR)/%$(e)): $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	export PATH=$(LEGACY_BLAST)/bin:$(PATH);export BLASTMAT=$(LEGACY_BLAST)/data;cd $(dir $@);$(call TPSI, $<)

$(SWISSPROT_BLAST_DIR)/%.asn: $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	$(call DELTABLAST, swissprot, $<, $@)

$(PDB_BLAST_DIR)/%.asn: $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	$(call DELTABLAST, pdb, $<, $@)

$(foreach e, $(DBCAN_EXTS), $(DBCAN_DIR)/%$(e)): $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	$(call HMMSCAN, $(dir $@)$(notdir $(basename $<)).out.dm, $<, $(dir $@)$(notdir $(basename $<)).out)
	$(call HMMSCAN_PARSER, $(dir $@)$(notdir $(basename $<)).out.dm, $(dir $@)$(notdir $(basename $<)).out.dm.ps)
