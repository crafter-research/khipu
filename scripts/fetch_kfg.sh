#!/bin/zsh
# Download Khipu Field Guide workbooks for every OKR khipu, one request per second, skipping existing files.
cd "${0:A:h}/../data/kfg" || exit 1
ok=0; miss=0
while read -r k; do
  [[ -s "$k.xlsx" ]] && { ok=$((ok+1)); continue; }
  code=$(curl -sL -w "%{http_code}" -o "$k.xlsx.part" "https://www.khipufieldguide.com/databook/excel_khipus/$k.xlsx")
  if [[ "$code" == "200" ]] && file "$k.xlsx.part" | grep -q "Excel"; then mv "$k.xlsx.part" "$k.xlsx"; ok=$((ok+1)); else rm -f "$k.xlsx.part"; echo "$k $code" >> missing.txt; miss=$((miss+1)); fi
  (( (ok+miss) % 50 == 0 )) && echo "progress ok=$ok miss=$miss"
  sleep 1
done < okr_nums.txt
echo "done ok=$ok miss=$miss"
