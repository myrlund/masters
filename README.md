Master's project
================

> The following is a draft of what will be the final project description. It is not necessarily up to date.

Personalizing anonymous video conferencing with machine learning and multivariate testing
-----------------------------

Identifying the different ways in which users use a product can be useful on several levels. In this project we will look at how identifying user classes allows for simple personalization of the product, and to what extent simple personalized treatments can alter user behavior.

It is often the case that some identified user classes are more desirable than others. Either because its associated users generate more revenue, use the product more, invite their friends, or similar. This project describes a system capable of not only identifying user classes, but more importantly a framework for identifying the most effective ways of driving users toward more desirable user classes.

More specifically, given a set of identified user classes and a set of predefined treatments, we want to find out how each treatment affects each user class. Although the project implementation will specifically target the video conferencing service appear.in, a major research question will be to what extent the results generalize.

Research questions
------------------

**Main research question:** Can users of anonymous video conferencing services be clearly divided into user classes based on their behavior, and if so, to what effect can personalisation improve their activity level?

1. Are users of video conferencing services such as appear.in clearly dividable into separate groups based only on their behavior within the service? Do these patterns reflect those seen elsewhere (in other types of internet services or IRL)?
2. Is it feasable to personalize treatments to these user classes? Does it stimulate users into becoming more active users?
    1. Is this something these users want?
    2. Do the inferred preferences of the detected user classes significantly differ from each other?
    3. Can the personalized treatments be devised in such a way as to stimulate the moving of users in the direction of any desired user class?
3. How can a toolkit be devised to handle the following?
    1. User classification based on behavior.
    2. Product personalization based on a relevant user's class.
    3. Tracking of each treatment's effect on each user class.
    4. Prioritize using the most effective treaments without introducing statistical bias (see [multi-armed bandit](http://en.wikipedia.org/wiki/Multi-armed_bandit)).
    5. Allow product developers to easily access results to improve future feature prioritization.

Possible treatments
-------------------

To be able to affect user behavior, actual differing treatments are required.

### High-level variations

- Varying availability of existing features.
- Toggling help texts for existing features.
- Hints on unused features.
- "Did you know?" on loading/alone.
- Simple poll question while loading/alone.
- Wording (claim/capture, appear/chat, room/office/channel)
    - Integrating with i18n

### Existing togglable features

- Text chat
- Claim room
- Follow room
- Customize room
- Kick

**A start could be to identify which ones are least used, and attempt to stimulate usage of those.**

### Possibly togglable features in the pipelines

- Localization
- Chat history

### New feature proposals

- Allow users to place arbitrary items in the room (notes, stickers, youtube-videos etc.)
- Nicknames
- Build in crowdsourcing of translations
