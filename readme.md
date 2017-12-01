California State University, Long Beach

CECS 327: Intro to Network and Distributed Systems

Professor: Anthony Giacolone

## Write up: Experience of project
Overall this project was really fun. I learned a lot about sockets. There were some issues with them but through trial and error and a lot of documentation reading, I figured it out. It was a nice feeling when I implemented the pinging. It was also nice to use a virtual machine. I had to put in a macOS on it. There were two main stages of my project.

Stage 1 was looking for IPs. At first, I wanted to keep pinging the network but then I realized I crashed the network. I then realized I can send the IP list and compare it with each other. I figured out how to ping by creating a lot of sub-processors to ping the network range from 1 – 255.

Stage 2 was connecting sockets and sending files to each other. At first, I was going to use JSON as the hash files but then I realized I can use a simple object key value pair. The key was the file name and the value was the modified time. This stage was a lot of debugging because I needed to see if files would send and if they would compare with each other. A big problem I came about was connecting sockets but that fix was done fairly fast.

Conclusion, I learned a lot in this project. I wish to continue this project possibly to optimize it even more. This project sparked my interest in backend code.