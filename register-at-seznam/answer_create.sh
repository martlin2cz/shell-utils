#!/bin/bash
#m@rtlin, 18. zari
#ze zadanoho seznmau slov vytvori posloupnost slov ("vetu") nahodne delky

#miniální délka vety
MINL=1

#maximalni delka vety
MAXL=8

WORDS=("Transformers" "John" "Jimmy" "Henry" "Hasselhoff" "Sea" "Block" "The" "The" "An" "A" "Book" "Smile" "Triple" "America"      "USA" "Hello" "Chuck Norris" "Internet" "On" "In" "From" "Hell" "Hi" "Japan" "Chinesse" "Sweet" "Love" "Chilli" "Curry" "Apple"       "Phone" "Space" "Joungle" "Ship" "Peter" "Paul" "Here" "Smith" "Springfiled" "New York" "OK" "True" "My" "Block" "Heavy" "Smell"      "Fun" "Fire" "Throw" "Catch" "Try" "No" "Not" "To" "Every" "Hard" "Die" "Kill" "Facebook" "Honey" "Music" "Books" "Team" "Oh" "Yea" "Yeah" "Fake" "Music" "..." "Smithers" "Home")
	  
len=$(($MINL + ($RANDOM % ($MAXL-$MINL))))

text=""

for ((index=0; index<len; index++)); do

	indx=$(($RANDOM % ${#WORDS[@]}))
	text=$text" "${WORDS[$indx]}" "

done

echo $text | sed 's/  / /g'

