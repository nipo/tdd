tsl_signed.xml:
	curl -i $@ https://ants.gouv.fr/files/25362bbf-a54e-4ed9-b98a-71e2382b54e0/tsl_signed.xml

FR*der: tsl_signed.xml:
	xpath -q -e '//tsl:TSPInformation/*[self::tsl:TSPInformationURI/tsl:URI/text() or self::tsl:TSPTradeName/tsl:Name/text()]' $< |awk '{if ($0 !~ /"fr"/) next; gsub(/.*">|<\/.*/, ""); if (x) {printf("wget -O %s.der \"%s\"\n", x, $0); x=""} else x=$0}'|sh -

# Unbundle DER from "multipart/mixed + chunked" response
# $ csplit --suppress-matched  -f '/tmp/' -b foo-%02d-file.der -z FR03.der $'/^--End\r/+1' '{*} && sed -ri '/^\r*$|--End/d' /tmp/foo*
# Get individual CN
# $ for i in /tmp/foo-*; do openssl x509 -in $i -inform DER -subject -nameopt multiline -nocert; done|grep commonName|sort |uniq -dc
