# About

This site is autogenerated every day using the latest information from both [mtggoldfish](https://www.mtggoldfish.com) (by default) and from [mtgtop8](http://mtgtop8.com) (secondary option). Essentially, each archetype is calculated to have a "stock" decklist, created by seeing what many different people have done and determining card synergizes, described in the algorithm below. This results in a "Best Version" decklist, which can be a very useful starting point for exploring an archetype, either for testing for tournaments or playing in them.

At the bottom of each page is a list of suggestions; these are cards that were cut during the course of deck construction. The higher up on the list the later the card was cut from the process. These are often good looks at other cards that you should consider when modifying the deck.

### Bannings and Format Rotation

Whenever a card is banned, it takes a while for the decklists where they were legal to be phased out of the history, so it's highly likely that the banned cards will still be present for a while. Once enough new decklists have been submitted then the generated decklists will stop showing the banned cards.

# Algorithm

Every time that the decklists updates, this is what happens:

1. Reads in all of the decklists provided
    1. For each combination of cards in the list, add that combination to a global pool of cards
        * For example, for a decklist of 1 Serum Visions, 1 Gitaxian Probe, and 1 Island, the combinations (for n = 2) added to the pool would be: (1 Serum Visions, 1 Gitaxian Probe), (1 Serum Visions, 1 Island), (1 Gitaxian Probe, 1 Island), (1 Serum Vision), (1 Gitaxian Probe), (1 Island)
    2. Cards that exist in multiples are each treated as their own card, with a positional order.
        * For example, 4 Serum Visions is treated like 4 separate cards: Serum Visions 1, Serum Visions 2, Serum Visions 3, and Serum Visions 4
    3. Each time that a combination repeats in a different decklist, the count for that combination is incremented by 1.
2. Start a loop until the number of cards left in the pool is the size of the deck (60 cards)
    1. Go through each combination in the pool
    2. For each card in the combination, increase the rank of that card by ``(number of times that the card appeared) * (1/2^(size of the combination))``
    3. Remove the card with the lowest rank
    4. Reset the rank of the card.
3. Repeat for sideboard

# Improvements

It's highly likely that there is a way to figure out what archetypes are listed as what on each site and merge the lists together. If you have an easy way to do so, please tell me.

# Offline Version

An offline version of this website, for personal use (such as giving it your own decklists instead of the mtgtop8 ones) can be found [here](https://github.com/MrTyton/deckbuilding).

# Suggestions

I don't do web programming really. If you have comments or suggestions or anything of the like, please open an issue in the github repo. Thank you!