"""
registration of a user 0 token
each user gets 10 tokens
store a sentence on out database for 1 token
retrieve his stored sentence for 1 token

API chart
Resource             |    Address      | Protocol  |   Param                       |  Response + Status
Register user        |    /register    | Post      | username password string      |  200 ok
store sentence       |  /store         | post      | username password sentence    |  200ok
                                                                                      301 no token
                                                                                      302 inv P & Un
retrieve sentence    | /get            | GET       | user n + p                    |  200 ok
                                                                                      301 no token
                                                                                      302 inv P and UN

"""