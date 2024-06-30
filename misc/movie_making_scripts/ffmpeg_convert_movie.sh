### https://stackoverflow.com/questions/5784661/how-do-you-convert-an-entire-directory-with-ffmpeg

### converting file format
### just drop this into the same directory as the movies whose formats you 
### want changed
for i in *.mov;
  do name=`echo "$i" | cut -d'.' -f1`
  echo "$name"
  ffmpeg -i "$i" "${name}.mp4"
done