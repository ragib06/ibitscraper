# InterviewBit Scraper

Scraper to extract **all** your codes in [InterviewBit Programming](https://www.interviewbit.com/courses/programming/) platform. It explores all the problem pages and extracts code from the editor. It stores the codes according to topics and cateogories in a local output directory. It also generates a csv file containing information about all the problems.

**CAUTION**: It will crawl **all** the problems, so if you don't want to open some problems, DO NOT run this script.


### Rrequirements: 
- pandas==0.25.1
- requests==2.22.0
- lxml==4.4.2
- Scrapy==1.8.0

* A *requirements.txt* file id provided. You can install the dependencies directly through it:

    ```pip install -r requirements.txt```


### Usage:

```
    sh run.sh [username] [password] [extension] [out_dir]
```

- [username]: Your InterviewBit username (email)
- [password]: Your InterviewBit password
- [extension]: File extension to your prefered programming language (i.e. "cpp")
- [out_dir]: Output directory to store results


### Output:

```
output
│   ibit_codes.csv                  <= csv with problems and (compressed) codes 
│   ibit_problems.csv               <= csv with problems
└───arrays
│   └───Arrangement
│       │   find-permutation.cpp    <= your code
│       │   largest-number.cpp
│       │   ...
│  
└───math
│   └───Number theory
│       │   greatest-common-divisor.cpp
│       │   ...
```

### Current Issues:

- Ignores the first (_Time Complexity_) and last (_Code Ninja!_) topic
- It'll crawl all the problems not the ones user is attempted
- If you haven't unlocked a specific topic, the behaviour is undefined


### Future Work:

- Extracting codes from the code editor is not always convenient, its better to extract from the previous submissions. That should be easily doable. I'm too lazy to do that for now. 
- Storing codes as compressed string is not great. A better option is to paste the code to some online code sharing sites and store the url to that permanent paste. Need a smooth API for that.



### Contact

Ragib Ahsan

rahsan3 AT uic DOT edu
