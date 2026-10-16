"""Audit a user-supplied map and explicitly assumed row drift radii."""
import argparse
import json
import numpy as np
from core import exposure_interval

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',help='JSON with weights, matrix, target_indices, radii')
    parser.add_argument('--refresh-count',type=int,default=3)
    args=parser.parse_args()
    if args.refresh_count<0:parser.error('refresh-count must be nonnegative')
    with open(args.input) as stream:data=json.load(stream)
    lo,hi,widths=exposure_interval(data['weights'],data['matrix'],data['target_indices'],data['radii'])
    order=np.argsort(-widths,kind='stable')[:args.refresh_count]
    print(json.dumps({'lower_share':lo,'upper_share':hi,'assumption':'Independent row TV balls at the supplied radii; no automatic coverage guarantee','refresh_row_indices':order.tolist(),'remaining_width_after_exact_refresh':max(0.,hi-lo-float(widths[order].sum()))},indent=2))
