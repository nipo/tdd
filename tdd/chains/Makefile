all: FR01.der  FR03.der  FR04.der  FR05.der

tsl_signed.xml:
	@echo "Fetching TSL"
	@curl -s -o $@ https://ants.gouv.fr/files/25362bbf-a54e-4ed9-b98a-71e2382b54e0/tsl_signed.xml

FR01.der  FR03.der  FR04.der  FR05.der: tsl_signed.xml
	@url=$$(xpath -q -e '//tsl:TSPTradeName[tsl:Name="$(subst .der,,$@)"]/../tsl:TSPInformationURI/tsl:URI[@xml:lang="fr"]/text()' $<) ; \
	echo "Fetching $@ from $${url}" ; \
	curl -s -o "$@" "$${url}"

clean:
	rm -f FR01.der  FR03.der  FR04.der  FR05.der tsl_signed.xml

# Unbundle DER from "multipart/mixed + chunked" response
# $ csplit --suppress-matched  -f '/tmp/' -b foo-%02d-file.der -z FR03.der $'/^--End\r/+1' '{*} && sed -ri '/^\r*$|--End/d' /tmp/foo*
# Get individual CN
# $ for i in /tmp/foo-*; do openssl x509 -in $i -inform DER -subject -nameopt multiline -nocert; done|grep commonName|sort |uniq -dc
