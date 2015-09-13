# HPU-experiments

<b>Developed for Aspiring Researchers Challenge, UC Santa Cruz + Stanford </b>

Python based GUI for placing human 'in the loop' for better classification.
The machine classified images are fed into the system which asks the users to
a) Remove False positives
b) Remove False Negatives

'Worker' is shown each bbox one after the other and is asked to classify them as correct or false using 'Y' or 'N'.
based on his response, the ordering of the images are dynamically updated to assist the work of the next worker.
The approach shows significant reduction in time taken by upcoming worker for contributing their vote towards the validity of the bounding box.

In the next round 'Workers' are asked to mark the False Negatives, further improving the results.

