import RAKE
import operator

stop_dir = "SmartStoplist.txt"
rake_object = RAKE.Rake(stop_dir,2,3,2)


text = """Google quietly rolled out a new way for Android users to listen 
to podcasts and subscribe to shows they like, and it already works on 
your phone. Podcast production company Pacific Content got the exclusive 
on it.This text is taken from Google news."""


# Extract keywords
keywords = rake_object.run(text)
print ("keywords: ", keywords)