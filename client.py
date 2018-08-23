import time
import json
import random
import string

from google.cloud import pubsub_v1

PROJECT = 'audotto'
TOPIC = 'ImageML-requests'
SUBSCRIPTION = 'ImageML-cli'

ACTION_UPLOAD = 'upload'
ACTION_CROP = 'crop'
ACTION_COMPARE = 'compare'
ACTION_SIMILAR = 'similar'

SAMPLE_IMAGE_URLS = [
    'http://eventive.in/wp-content/uploads/2016/07/sample-person.jpg',
    'http://www.spoorcongres.nl/wp-content/uploads/2018/06/person_sample_3.jpg',
    'https://avada.theme-fusion.com/wp-content/uploads/2015/09/person_sample_2.jpg',
]

COMPARE_DATA = {
	"first_data": 
	{'object': [{'object_name': 'person', 'processing_idx': '0', 'ssim': '<PIL.Image.Image image mode=RGB size=256x256 at 0x7FC4841F8860>', 'hash': 'eca442228002821', 'hist': '[[[1.62103318e-03 1.62103315e-05 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]]\n\n [[2.45424416e-02 1.45892991e-04 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [1.06501877e-02 2.56285332e-02 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]]\n\n [[9.88830230e-04 3.24206630e-05 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [1.59671772e-02 8.09381828e-02 6.48413261e-05 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 1.43461432e-02 9.40199196e-03 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]]\n\n [[1.62103315e-05 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [3.03133205e-03 1.69560071e-02 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [2.75575643e-04 6.48575351e-02 7.30761737e-02 3.24206630e-05\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 9.17504728e-03 2.75575626e-03\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]]\n\n [[0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 3.40416969e-04 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [8.10516576e-05 4.69289087e-02 2.48342287e-02 1.62103315e-05\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 1.37625718e-02 1.24187350e-01 4.82095256e-02\n   3.24206630e-05 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 1.01638781e-02\n   4.60373424e-03 4.86309946e-05 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]]\n\n [[0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 1.94523978e-04 2.12355354e-03 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 1.75071578e-03 1.01184890e-01 2.88868099e-02\n   8.10516576e-05 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 2.75413524e-02 1.21512644e-01\n   7.18604028e-02 2.48018070e-03 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 9.72619891e-05\n   1.64534859e-02 4.46756743e-02 2.57744268e-03 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]]\n\n [[0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 1.02125085e-03 5.67361596e-04\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 4.02016239e-03 7.60264546e-02\n   4.55510337e-03 6.48413261e-05 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 2.00521797e-02\n   7.27195442e-02 3.31987590e-02 3.77700734e-03 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   8.10516576e-05 1.74098965e-02 3.96666825e-02 9.07778565e-04]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 4.86309946e-05 5.34940918e-04]]\n\n [[0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 1.29682652e-04\n   0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 4.86309931e-04\n   4.21468634e-04 0.00000000e+00 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 1.29682652e-03\n   4.42704149e-02 4.71720658e-03 0.00000000e+00 0.00000000e+00]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   4.71720658e-03 6.44847006e-02 4.26007509e-02 4.37678944e-04]\n  [0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00\n   0.00000000e+00 9.72619891e-05 2.08302755e-02 9.50654864e-01]]]', 'lbp': '[0.0190652  0.02099677 0.01049509 0.00864263 0.00707364 0.00826027\n 0.00767354 0.01124003 0.01211682 0.01849166 0.02394357 0.03828202\n 0.04813765 0.0506955  0.02152416 0.02142528 0.01236074 0.0204496\n 0.00988859 0.01840596 0.01481311 0.02217681 0.01981014 0.02878898\n 0.08806118 0.43718109]', 'identificator': 'F0CD0V6UJTNROZR34UWSBQ6FKATOGNEU42022G4N36EL5VXNUDB1BWSN6FPGVYOIAASJ1FBJF0YQR3VK7XEPQYCJWBP78NDP6APD'}], 'version': [{'Name': 'compare-ml', 'version': '1.0.1'}]},
	"second_data": 
	{'object': [{'object_name': 'person', 'processing_idx': '0', 'ssim': '<PIL.Image.Image image mode=RGB size=256x256 at 0x7FC4841DD978>', 'hash': 'a56040c60230140', 'hist': '[[[1.1708121e-03 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]]\n\n [[2.3845538e-02 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [1.4088772e-02 1.5805963e-02 3.0831385e-03 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 2.4587053e-03 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]]\n\n [[7.8054139e-04 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [1.0537309e-02 5.5652600e-02 1.3269203e-03 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 1.1044661e-02 4.9759515e-02 1.4322935e-02 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 6.2443310e-04 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]]\n\n [[0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [2.7318948e-04 5.7369792e-03 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 3.0402087e-02 4.7925241e-02 1.8342723e-03 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 7.9224948e-03 2.7709220e-02 3.0831385e-03\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 3.9027069e-05 2.3416241e-04\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]]\n\n [[0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 1.9513535e-04 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 6.1272499e-03 2.0255048e-02 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 3.7661120e-02 3.0441113e-02 2.6538407e-03\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 3.3173009e-03 4.3983508e-02\n   4.9174107e-03 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 3.9027069e-05\n   2.3416241e-03 7.8054138e-05 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]]\n\n [[0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 2.3416241e-04 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 4.8783835e-02 4.9603406e-02 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 7.8054138e-05 1.0002638e-01 2.5133433e-02\n   1.0068984e-02 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 6.4394665e-03\n   4.1723838e-01 7.2590350e-03 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   1.5610828e-04 2.2635700e-03 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]]\n\n [[0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 3.9027069e-05 1.2488662e-03 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 9.2494152e-02 9.3703993e-02\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 7.8054138e-05 8.1098251e-02\n   7.7390678e-02 5.0540052e-02 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   1.1825202e-02 8.1254357e-01 4.2539503e-02]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 6.0882228e-03 8.4688738e-03]]\n\n [[0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 7.6493053e-03\n   1.5064448e-02 0.0000000e+00 0.0000000e+00]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   3.6295175e-03 7.9342030e-02 1.3815583e-02]\n  [0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00 0.0000000e+00\n   0.0000000e+00 6.3965365e-02 2.9781556e-01]]]', 'lbp': '[0.03250134 0.02416801 0.01668009 0.01552603 0.01391573 0.01474772\n 0.01449275 0.01582126 0.01555287 0.0189211  0.0229737  0.03447397\n 0.05       0.04778583 0.02105475 0.01635802 0.01320451 0.01545894\n 0.01148685 0.01453301 0.01123188 0.0157139  0.01555287 0.02475845\n 0.03470209 0.46838433]', 'identificator': '99VFCJ94KYC39O8OK1Z39LFY4L5JXPU9A8A0PGJOTQC9I0ZZ8BXY5MY9XTFMZ5OZFJ84GL1QIYCN3LXJCJPDTOD6685UC6L1TYZW'}], 'version': [{'Name': 'compare-ml', 'version': '1.0.1'}]}
}

def publish_message(message):
    """Publishes multiple messages to a Pub/Sub topic."""

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT, TOPIC)

    message = message.encode('utf-8')
    publisher.publish(topic_path, data=message)

    print('Published messages.\n\t{}\n'.format(message))
    
def receive_messages():
    """Receives messages from a pull subscription."""

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        PROJECT, SUBSCRIPTION)

    def callback(message):
        msg = json.loads(message.data.decode('utf-8'))
        print('Received message: {}'.format(msg))
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)

    print('Listening for messages on {}'.format(subscription_path))
    while True:
        time.sleep(3)

def make_message(action, data):
    message = {}
    message['action'] = action
    message['data'] = data
    return json.dumps(message)

def publish_upload_messages():
    for image_url in SAMPLE_IMAGE_URLS:
        data = {}
        data['image_url'] = image_url
        data['identificator'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))
        msg = make_message(ACTION_UPLOAD, data)
        publish_message(msg)

def publish_crop_messages():
    for image_url in SAMPLE_IMAGE_URLS:
        msg = make_message(ACTION_CROP, image_url)
        publish_message(msg)

def publish_compare_messsage():
    msg = make_message(ACTION_COMPARE, COMPARE_DATA)
    publish_message(msg)

def publish_similar_messsage():
    msg = make_message(ACTION_SIMILAR, COMPARE_DATA)
    publish_message(msg)

if __name__ == '__main__':
    # publish_upload_messages()
    # publish_crop_messages()
    publish_compare_messsage()
    publish_similar_messsage()

    receive_messages()