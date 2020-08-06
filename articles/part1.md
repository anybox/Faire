# Part 1 Let's dive in, shall we ?

### Method

I have a confession to make. I have struggle not being clueless when someone
explains something to me. Not that I'm dumb or anything (my mum says I'm 
special), rather, I have the attention span of a young hamster.

The way I like things explained to me is: going through __ONE__ concept, and
once I fully get it, building upon it. 

Here's how I'm going to proceed for every concept I'll tackle:
* Explain as clearly and thoroughly as possible 
* Write tests, to define specifications 
* Write the dummyest implementation possible to pass the tests
* Keep the proper implementation as a __TODO__ for future parts

### Core concepts (First batch)
#### Foreword

I'll go through the main concepts we'll use in this part.
Depending what your current familiarity with those concept is
at the moment, that may be a lot of information to process.

It'll become clearer at implementation.

#### Functional decomposition

When code began to be a thing, the only aim of coders was to make 
stuff work as intended.

While that's obviously still what you want for your code, things
have changed. Applications' complexity has grown exponentially and
unless the problem you want to solve is super simple (in which case
you're building a __script__ rather than an application), going heads
down and writing a fat blob of code will very quickly result in 
something totally unbearable.

(Side note: if you're interested in history of the idea of "clean 
code", this article is more or less its birth: 
[Goto statement considered harmful](https://homepages.cwi.nl/~storm/teaching/reader/Dijkstra68.pdf))


__Functional decomposition__ comes to ou rescue.

To put it simply, imagine your application as a set of __bricks__. 
Each brick should do ONE thing. Bricks are then used as the building 
block of more complex bricks and so on.


#### Unit test & TDD

To go a bit into technicalities (but that's a side note, you can skip it)
you have mainly two approach for a code to be tested:
* __Maths__: Your code can be proven right. Fun fact: that relies on 
programming paradigm (lambda calculus) that predates programming, even computer
* __Science__: Your code can (and that's waaaay more convenient than the 
previous approach) be tested with enough variety of inputs that it's fair to
assume it works as intended.

I have little -if any- clues about how to make provable code. We'll (as mostly
every one else using tests) go for the second.


So, to come back to our subject. A unit test is a function that will take one
of the aformentioned brick (a function). Give that function inputs, and test
whether or not it returns what we want it to return.

If you're not familiar yet with unit tests, don't panic, I'll detail each
step.

__TDD__ is the acronym of Test Driven Development. It simply describes the
process of writing the tests before what's to be tested.


#### Event Sourcing




#### Immutability
#### Event Store

