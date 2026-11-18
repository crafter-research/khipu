#!/bin/zsh
# Download KFG pendant-pendant sum pages, one request per second, skipping existing files.
cd "${0:A:h}/../data/kfg_sums" || exit 1
n=0
while read -r k; do
  [[ -s "$k.html" ]] && continue
  code=$(curl -sL -w "%{http_code}" -o "$k.html.part" "https://www.khipufieldguide.com/notebook/fieldmarks/pendant_pendant_sum/html/$k.html")
  if [[ "$code" == "200" ]]; then mv "$k.html.part" "$k.html"; else rm -f "$k.html.part"; echo "$k $code" >> missing.txt; fi
  n=$((n+1)); (( n % 100 == 0 )) && echo "progress $n"
  sleep 1
done < ../kfg/okr_nums.txt
echo "done"
