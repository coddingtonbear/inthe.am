for screenshot in /tmp/*.png
do
    travis-artifacts upload --path "$screenshot"
done
for screenshot in /tmp/*.html
do
    travis-artifacts upload --path "$screenshot"
done
