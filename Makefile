C=$(shell pwd)
PYTHON=python
IPS=/usr/local/interproscan/5.15-54.0/interproscan-5.15-54.0/interproscan.sh
TMHMM=/usr/local/tmhmm/2.0c/bin/tmhmm
LEGACY_BLAST=/home/darcy/bin/blast-2.2.26
DATA=$(C)/data
PROT_FILE=I5V.codingquarry.faa
ISOLATE=$(word 1, $(subst ., ,$(PROT_FILE)))
THREADS=1


SPLITTER=$(PYTHON) $(C)/lib/splitter.py -i $(1) -p $(2) -n $(3)
IPS=@echo /usr/local/interproscan/5.15-54.0/interproscan-5.15-54.0/interproscan.sh -f TSV,XML,GFF3,HTML,SVG --goterms -dp --iprlookup --pathways -t p -i $(1) --output-dir $(2)
SIGNALP=signalp -f short -n $(1) -l $(2) < $(3) > $(4)
TMHMM=/usr/local/tmhmm/2.0c/bin/tmhmm < $(1) > $(2)
TARGETP=targetp -c -$(1) < $(2) > $(3)
TPSI=/usr/local/transposonpsi/08222010/transposonPSI.pl $(1) prot
DELTABLAST=deltablast -query $(1) -out $(2) -db refseq_protein -outfmt 11 -num_threads $(THREADS) -use_sw_tback

BLOCK_SIZE=1000
NSEQS = $(shell grep -c '>' $(1))
NBLOCKS = $(shell python -c "from math import ceil;print(int(ceil($(1) / $(2).)))")
RANGE = $(shell echo {1..$(call NBLOCKS, $(1), $(BLOCK_SIZE))})
SPLIT_FNAMES = $(foreach i, $(call RANGE, $(call NSEQS, $(1))), $(addsuffix -$(i).fasta, $(2)))



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

DBLAST_DIR=$(C)/deltablast
DBLAST_FILES=$(foreach f, $(SPLIT_FILES), $(DBLAST_DIR)/$(addsuffix .asn, $(notdir $(f))))


all: split signalp tmhmm targetp transposonpsi

#deltablast
#interproscan

split: $(SPLIT_FILES)
interproscan: $(IPS_FILES)
signalp: $(SIGNALP_FILES)
tmhmm: $(TMHMM_FILES)
targetp: $(TARGETP_FILES)
transposonpsi: $(TPSI_FILES)
deltablast: $(DBLAST_FILES)

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

$(DBLAST_DIR)/%.asn: $(SPLIT_DIR)/%
	mkdir -p $(dir $@)
	$(call DELTABLAST, $<, $@)
