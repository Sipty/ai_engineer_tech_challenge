# Live demo:
https://www.loom.com/share/eec9762591c04657aeadd7e6b64feb4a?sid=ff72a2f7-3b76-4f80-93c6-36fee65c7fc9

# Chavdar's awesome chatbot
This was an incredibly fun project - thank you for the opportunity and I hope the following words will not be too rambly, while still conveying my design intentions, problems faced and lines in the sand I eventually had to draw.

I've left the original requirements at the very bottom, as a guide for both writer and reader of the original goal.

Initially I took on this project and did not ask for further clarifications on constraints, since I wanted to really impress with how much I can overdeliver. In fact, this was my personal challenge ontop of the challenge. In a real world scenario, the below would be challenged and picked apart until every single feature is clearly defined and signed off on.

With that said - how did I approach this problem? Same way I approach any other - break the problem down into the smallest tangible chunk, consider the implementation details and get on it. In fact, if you go over the commit history, this is clearly visible (up until I hit cloud deployment - will touch on that later).

The problem itself is not too challenging - create a full stack app MVP with an LLM generating text. I started by building up the LLM string returner module, which I called chat. It's the simplest form of an LLM I could muster - feed prompts into a model. The repliest were so horrific, I decided to add some extra example generation, just to guide it a bit. That worked nicely, apart from the wild tangents it was going on. For this, I added simple string cutting after the first informative sentence, ie . or ! and said it was good enough.

Next I built the API - initially it was a directly prompt to the chat (which worked nicely). I've been in love with FastAPI for prototyping lately, so I used it in this project as well. One the basics were out the door, I continued to the frontend: a simple chat window. 

And that was all she wrote really - the project was 90% complete. But I was determined to really over deliver, remember? So I started with frontend and made it extra snazzy, with a rolling chat box and gave it a lick of paint. 

Next was the API - I knew what I had built was good enough for an MVP, but that was not really enough. So I split the API in two and added a message queue between the api and the chat. In my mind, I was visualising how all of this would live in ECS/ the real world, ie:

User types message -> Send message to API and get a message token back
API sends message to RabbitMQ with message token, while also returning the token
When chat is ready -> puts message into queue with token 
React continuously polls API for a response -> API checks RabbitMQ for messages with that token.

The token is currently stored in the API as a hashmap for simplicity, but in the real world that would be held in Redis to reduce coupling and load on the API.

With that small exception, the architecuture is fully ready to be scalled horizontally. I was not satisfied with the possibility of pursuing vertical scaling for this, as the chat would scale the replicas required to 1 per user... Which we obviously dont want :)

Around this time I realised localstack has severe limitations to its AWS service functionality. I wanted to use ECR for container storage, ECS for a simple cluster, ELB for a load balancer and CloudWatch for monitoring.. It was going to be glorious. And then I realised all of those features are payed for T_T. So I drew a line in the sand and decided to go for a local setup. I was/ am adamant about fulfilling all requirements - so despite everything working on the local network, I decided to push for a solution that would translate to reality even more closely - so I decided to go for the classic local development 'cloud' of docker compose up, which also satisfied the IEC requirement and the load balancing stretch goal, as its a single button to rule them all. At this point, I had invested way more than a homework challenge should ask of anyone.. But as I mentioned above - I was/ am determined to add as much spit and polish as possible before the arbitrary deadline of 'Sunday'. So I continued pushing - lets use a 'cloud-cloud' solution:

## Dockerswarm

This is where I hit my roadblock - in fact, I am still not 100% satisfied with this solution and I'll explain why:

Once I started pushing my stack to the swarm, my API calls started failing! After a lot of debugging, it turned out to be a CORS issue. In fact, there will likely be artifacts left in the code, even after the cleanup I did, hinting at my struggles with this. For whatever reason, my browser insitently refused to allow API calls to an internal IP address. And how do I know this? Well, just look at the current implementation of ChatBox (frontend/src/componentsChatBox.jsx) - it calls my WSL's ip address. This was the only way to get my browser to allow this - any other attempts would resolve to localhost, despite the stack living in the swarm under my WSL linux box. I have lost so many braincells trying to debug this (and I was going to continue doing so) until I found an article mentioning this was blocked by all major browsers (including by my adblocker!). It was this moment that really got my to appreciate having a teammate around for such technical problems. It was a fun issue to unpeel in any case!

# Future improvements

## GoogleBox
I did have a few stretch goals in mind, in case time permitted. I was planning on adding in a 'GoogleBox' component, which would show the most relevant website served by google for a specific query - similar to perplexity's interface. I was going to use beautiful soup to grab the text, summary, images needed to build it. I was also imagining adding the synopsis to the prompt as a fairly cheap additional context.

## Chat history
Chat history and user accounts was another thing I wanted to do. Similar to how similar chatbots function. A stretch of this stretch would've been projects, similar to how Claude implements them. I think it would've been cool to try and retain additional context of conversations for more pizzaz.


# Original requirements:
Subject of this challenge is to develop and deploy a simple, but production ready replica of [Perplexity.ai](https://www.perplexity.ai/).

The requirements are as follows:
* Feel free to use any open-source framework : LlamaIndex, LangChain, Haystack, etc.
* Basic UI.
* Any LLM.
* Any Cloud.
* Should be deployable with scripts (IaC)
* Think about scalability and performance.<br>



Helpers:

- IaC Test account:
  - AWS Free Tier account: <https://aws.amazon.com/free/>
  - Localstack API: <https://localstack.cloud>
- Terraform best practices: <https://cloud.google.com/docs/terraform/best-practices-for-terraform>
- Terraform AWS provider: <https://registry.terraform.io/providers/hashicorp/aws/latest>
- LlamaIndex: <https://www.llamaindex.ai/>
- LangChain: <https://www.langchain.com/>
- Streamlit: <https://streamlit.io/>
- Loom: <https://www.loom.com/>
