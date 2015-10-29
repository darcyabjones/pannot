C=$(shell pwd)
DATA=$(C)/data
PROT_FILE=B04.protein.faa
ISOLATE=$(word 1, $(subst ., ,$(PROT_FILE)))
EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

go=$(DATA)/go-basic.obo
goslim=$(DATA)/goslim_generic.obo
PANTHERFAMCLASS=$(DATA)/PANTHER10.0_HMM_classifications
domain2go=$(DATA)/Domain2GO_supported_only_by_all.txt
hamap2go=$(DATA)/hamap2go
interpro2go=$(DATA)/interpro2go
pfam2go=$(DATA)/pfam2go
pirsf2go=$(DATA)/pirsf2go
prints2go=$(DATA)/prints2go
prodom2go=$(DATA)/prodom2go
prosite2go=$(DATA)/prosite2go
smart2go=$(DATA)/smart2go
tigrfams2go=$(DATA)/tigrfams2go


THREADS=1
PYTHON=python
LEGACY_BLAST=/home/darcy/bin/blast-2.2.26
BLAST_COLS=qseqid qlen sallseqid sgi sacc saccver slen qstart qend sstart send qseq sseq evalue bitscore score length pident nident mismatch positive gapopen gaps ppos frames qframe sframe btop staxids sscinames scomnames sblastnames sskingdoms stitle salltitles sstrand qcovs qcovhsp

SPLITTER=$(PYTHON) $(C)/bin/splitter.py -i $(1) -p $(2) -n $(3)
IPS=@echo /usr/local/interproscan/5.15-54.0/interproscan-5.15-54.0/interproscan.sh -f TSV,XML,GFF3,HTML,SVG --goterms -dp --iprlookup --pathways -t p -i $(1) --output-dir $(2)
SIGNALP=signalp -f short -n $(1) -l $(2) < $(3) > $(4)
TMHMM=/usr/local/tmhmm/2.0c/bin/tmhmm < $(1) > $(2)
TARGETP=targetp -c -$(1) < $(2) > $(3)
RENAME=$(PYTHON) $(C)/bin/rename_fasta.py -i $(1) -o $(2) -j $(3)
SECRETOMEP=/usr/local/secretomep/1.0/secretomep
TPSI=/usr/local/transposonpsi/08222010/transposonPSI.pl $(1) prot
DELTABLAST=deltablast -db $(1) -query $(2) -out $(3) -outfmt 11 -num_threads $(THREADS) -use_sw_tback
HMMSCAN=hmmscan --domtblout $(1) $(DATA)/dbCAN-fam-HMMs.txt $(2) > $(3)
HMMSCAN_PARSER=hmmscan-parser.sh $(1) > $(2)
BLAST_FORMATTER=blast_formatter -archive $(1) -out - -outfmt '6 $(BLAST_COLS)'
LOCATORP=$(C)/bin/locatorp.py -s $(1) -e $(2) -t $(3) -a $(4) -o $(5)
PANTHERFAMS=$(C)/bin/get_panther_fams.py -i $(1) -o $(2) -p $(3)
GETGOS=$(C)/bin/get_gos.py -i $(1) -o $(2) --obofile $(go)\
		--pantherfile $(PANTHERFAMCLASS) --pfamfile $(pfam2go) --smartfile $(smart2go)\
		--interprofile $(interpro2go) --prositefile $(prosite2go) --printsfile $(prints2go)\
		--prodomfile $(prodom2go) --tigrfamfile $(tigrfams2go) --pirsffile $(pirsf2go)\
		--hamapfile $(hamap2go) --domainfile $(domain2go)
GOLONG2ASSOC=$(C)/bin/golong2assoc.py -i $(1) -o $(2)
GOASSOC2LONG=$(C)/bin/goassoc2long.py -i $(1) -o $(2) --obofile $(go)
MAP_TO_SLIM=map_to_slim.py --association_file=$(1) $(go) $(goslim)

BLOCK_SIZE=1000
NSEQS = $(shell grep -c '>' $(1))
NBLOCKS = $(shell python -c "from math import ceil;print(int(ceil($(1) / $(2).)))")
RANGE = $(shell echo {1..$(call NBLOCKS, $(1), $(BLOCK_SIZE))})
SPLIT_FNAMES = $(foreach i, $(call RANGE, $(call NSEQS, $(1))), $(addsuffix -$(i).fasta, $(2)))

## Define filenames and directories

SPLIT_DIR = $(C)/split_aa
SPLIT_FILES = $(call SPLIT_FNAMES, $(DATA)/$(PROT_FILE), $(SPLIT_DIR)/$(ISOLATE))

IPS_DIR = $(C)/interproscan
IPS_EXTS=.tsv .xml .gff3 .html .svg
IPS_FILES = $(foreach e, $(EXTS), $(foreach f, $(SPLIT_FILES), $(IPS_DIR)/$(notdir $(f))$(e)))
IPS_CMB_TSV_FILE=$(IPS_DIR)/$(ISOLATE).combined.tsv

SIGNALP_DIR=$(C)/signalp
SIGNALP_FILES=$(foreach f, $(SPLIT_FILES), $(SIGNALP_DIR)/$(addsuffix .signalp.out, $(notdir $(f))))
SIGNALP_CMB_FILE=$(SIGNALP_DIR)/$(ISOLATE).combined.signalp.out

TMHMM_DIR=$(C)/tmhmm
TMHMM_FILES=$(foreach f, $(SPLIT_FILES), $(TMHMM_DIR)/$(addsuffix .tmhmm.out, $(notdir $(f))))
TMHMM_CMB_FILE=$(TMHMM_DIR)/$(ISOLATE).combined.tmhmm.out

TARGETP_DIR=$(C)/targetp
TARGETP_EXTS=.targetp.npn.out .targetp.pn.out
TARGETP_FILES=$(foreach e, $(TARGETP_EXTS), $(foreach f, $(SPLIT_FILES), $(TARGETP_DIR)/$(addsuffix $(e), $(notdir $(f)))))
TARGETP_CMB_PN_FILE=$(TARGETP_DIR)/$(ISOLATE).combined.targetp.pn.out
TARGETP_CMB_NPN_FILE=$(TARGETP_DIR)/$(ISOLATE).combined.targetp.npn.out

SECRETOMEP_DIR=$(C)/secretomep
SECRETOMEP_FILES=$(foreach f, $(SPLIT_FILES), $(SECRETOMEP_DIR)/$(addsuffix .out, $(notdir $(f))))
SECRETOMEP_CMB_FILE=$(SECRETOMEP_DIR)/$(ISOLATE).combined.secretomep.out

TPSI_DIR=$(C)/tpsi
TPSI_EXTS=.TPSI.allHits .TPSI.topHits
TPSI_FILES=$(foreach e, $(TPSI_EXTS), $(foreach f, $(SPLIT_FILES), $(TPSI_DIR)/$(addsuffix $(e), $(notdir $(f)))))
TPSI_CMB_FILE=$(TPSI_DIR)/$(ISOLATE).combined.TPSI.topHits

SWISSPROT_BLAST_DIR=$(C)/swissprot_deltablast
SWISSPROT_BLAST_FILES=$(foreach f, $(SPLIT_FILES), $(SWISSPROT_BLAST_DIR)/$(addsuffix .asn, $(notdir $(f))))
SWISSPROT_CMB_TSV_FILE=$(SWISSPROT_BLAST_DIR)/$(ISOLATE).combined.tsv

PDB_BLAST_DIR=$(C)/pdb_deltablast
PDB_BLAST_FILES=$(foreach f, $(SPLIT_FILES), $(PDB_BLAST_DIR)/$(addsuffix .asn, $(notdir $(f))))
PDB_CMB_TSV_FILE=$(PDB_BLAST_DIR)/$(ISOLATE).combined.tsv


DBCAN_DIR=$(C)/dbCAN
DBCAN_EXTS=.out .out.dm .out.dm.ps
DBCAN_FILES=$(foreach e, $(DBCAN_EXTS), $(foreach f, $(SPLIT_FILES), $(DBCAN_DIR)/$(addsuffix $(e), $(notdir $(f)))))
DBCAN_CMB_FILE=$(DBCAN_DIR)/$(ISOLATE).combined.out.dm.ps

LOCATION_DIR=$(C)/location
LOCATION_FILE=$(LOCATION_DIR)/$(ISOLATE).location.tsv

PANTHER_DIR=$(C)/panther_terms
PANTHER_FILE=$(PANTHER_DIR)/panther_fams.tsv

GOTERMS_DIR=$(C)/goterms
GOTERMS_FILE=$(GOTERMS_DIR)/goterms.tsv
GOSLIMTERMS_FILE=$(GOTERMS_DIR)/goslimterms.tsv

## Commands
all: split signalp tmhmm targetp transposonpsi swissprot pdb secretomep \
	dbcan interproscan pantherfams goterms

#interproscan

split: $(SPLIT_FILES)
interproscan: $(IPS_FILES) $(IPS_CMB_TSV_FILE)
signalp: $(SIGNALP_FILES) $(SIGNALP_CMB_FILE)
tmhmm: $(TMHMM_FILES) $(TMHMM_CMB_FILE)
targetp: $(TARGETP_FILES) $(TARGETP_CMB_PN_FILE) $(TARGETP_CMB_NPN_FILE)
secretomep: $(SECRETOMEP_FILES) $(SECRETOMEP_CMB_FILE)
transposonpsi: $(TPSI_FILES) $(TPSI_CMB_FILE)
swissprot: $(SWISSPROT_BLAST_FILES) $(SWISSPROT_CMB_TSV_FILE)
pdb: $(PDB_BLAST_FILES) $(PDB_CMB_TSV_FILE)
dbcan: $(DBCAN_FILES) $(DBCAN_CMB_FILE)
locatorp: $(LOCATION_FILE)
pantherfams: $(PANTHER_FILE)
goterms: $(GOTERMS_FILE) $(GOSLIMTERMS_FILE)

$(SPLIT_FILES): $(DATA)/$(PROT_FILE)
	rm -f $(dir $@)*
	@mkdir -p $(dir $@)
	$(call SPLITTER, $<, $(dir $@)$(ISOLATE), $(BLOCK_SIZE))
	sed -i -e 's/\*//g' $(SPLIT_FILES)

$(foreach e, $(IPS_EXTS), $(IPS_DIR)/%$(e)): $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	$(call IPS, $<, $(dir $@))

$(IPS_CMB_TSV_FILE): $(filter-out $(IPS_CMB_TSV_FILE), $(IPS_DIR)/*.tsv)
	cat $^ > $@

$(SIGNALP_DIR)/%.signalp.out: $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	$(call SIGNALP, $(basename $@).gff3, $(basename $@).log, $<, $@)

$(SIGNALP_CMB_FILE): $(SIGNALP_FILES)
	awk '!/^#/ && !/^$$/' $^ > $@

$(TMHMM_DIR)/%.tmhmm.out: $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	cd $(dir $@);$(call TMHMM, $<, $@)

$(TMHMM_CMB_FILE): $(TMHMM_FILES)
	cat $^ > $@

$(TARGETP_DIR)/%.targetp.npn.out: $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	$(call TARGETP,N, $<, $@)

$(TARGETP_CMB_NPN_FILE): $(filter-out $(TARGETP_CMB_NPN_FILE), $(TARGETP_DIR)/*.targetp.npn.out)
	echo '' > $@
	$(foreach f, $^, head -n -1 $(f)|awk '/^-/{flag=0}flag;/^-/{flag=1;next}' >> $@;)

$(TARGETP_DIR)/%.targetp.pn.out: $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	$(call TARGETP,P, $<, $@)

$(TARGETP_CMB_PN_FILE): $(filter-out $(TARGETP_CMB_PN_FILE), $(TARGETP_DIR)/*.targetp.pn.out)
	echo '' > $@
	$(foreach f, $^, sed '$$d' $(f)|awk '/^-/{flag=0}flag;/^-/{flag=1;next}' >> $@;)

$(SECRETOMEP_DIR)/%.out: $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	$(call RENAME, $<, -, $@.json)|$(call SECRETOMEP) > $@.tmp
	$(call RENAME, $@.tmp, $@, $@.json) -d
	rm $@.tmp $@.json

$(SECRETOMEP_CMB_FILE): $(SECRETOMEP_FILES)
	 awk '!/^#/ && !/^$$/' $^ > $@

$(foreach e, $(TPSI_EXTS), $(TPSI_DIR)/%$(e)): $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	export PATH=$(LEGACY_BLAST)/bin:$(PATH);export BLASTMAT=$(LEGACY_BLAST)/data;cd $(dir $@);$(call TPSI, $<)

$(TPSI_CMB_FILE): $(filter-out $(TPSI_CMB_FILE), $(TPSI_DIR)/*.TPSI.topHits)
	awk '!/^\/\// && !/^$$/' $^ > $@

$(SWISSPROT_BLAST_DIR)/%.asn: $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	$(call DELTABLAST, swissprot, $<, $@)

$(SWISSPROT_CMB_TSV_FILE): $(SWISSPROT_BLAST_FILES)
	echo "$(subst $(SPACE),	,$(BLAST_COLS))" > $@
	$(foreach f, $^, $(call BLAST_FORMATTER, $(f)) >> $@;)

$(PDB_BLAST_DIR)/%.asn: $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	$(call DELTABLAST, pdbaa, $<, $@)

$(PDB_CMB_TSV_FILE): $(PDB_BLAST_FILES)
	echo "$(subst $(SPACE),	,$(BLAST_COLS))" > $@
	$(foreach f, $^, $(call BLAST_FORMATTER, $(f)) >> $@;)

$(foreach e, $(DBCAN_EXTS), $(DBCAN_DIR)/%$(e)): $(SPLIT_DIR)/%
	@mkdir -p $(dir $@)
	$(call HMMSCAN, $(dir $@)$(notdir $(basename $<)).out.dm, $<, $(dir $@)$(notdir $(basename $<)).out)
	$(call HMMSCAN_PARSER, $(dir $@)$(notdir $(basename $<)).out.dm, $(dir $@)$(notdir $(basename $<)).out.dm.ps)

$(DBCAN_CMB_FILE): $(filter-out $(DBCAN_CMB_FILE), $(DBCAN_DIR)/*.out.dm.ps)
	cat $^ > $@

$(LOCATION_FILE): $(SIGNALP_CMB_FILE) $(SECRETOMEP_CMB_FILE) $(TMHMM_CMB_FILE) $(TARGETP_CMB_NPN_FILE)
	@mkdir -p $(dir $@)
	$(call LOCATORP, $(word 1, $^), $(word 2, $^), $(word 3, $^), $(word 4, $^), $@)

$(PANTHER_FILE): $(IPS_CMB_TSV_FILE) $(PANTHERFAMCLASS)
	@mkdir $(dir $@)
	$(call PANTHERFAMS, $(word 1, $^), $@, $(word 2, $^))

$(GOTERMS_FILE): $(IPS_CMB_TSV_FILE)
	@mkdir -p $(dir $@)
	$(call GETGOS, $<, $@)

$(GOSLIMTERMS_FILE): $(GOTERMS_FILE)
	@mkdir -p $(dir $@)
	$(call GOLONG2ASSOC, $<, $<.assoc)
	$(call MAP_TO_SLIM,$<.assoc)|$(call GOASSOC2LONG, -, $@)
	@rm -f $<.assoc
	@rm -f $@.assoc
