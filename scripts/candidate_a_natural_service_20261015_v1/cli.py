"""Explicit card preparation/release entry; importing never starts SUMO."""
import argparse
import json
from src.candidate_a_natural_service_20261015 import profile


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('prepare','validate','execute'))
    parser.add_argument('--card')
    parser.add_argument('--release')
    args=parser.parse_args()
    if args.action=='prepare':
        card=profile.prepare()
        print(json.dumps(dict(status='PREPARED_NOT_RELEASED',card=str(card),sha256=profile.sha(card))))
        return 0
    parser.error('card and exact release are required') if not args.card or not args.release else None
    if args.action=='validate':
        profile.validate_release(args.card,args.release)
        print(json.dumps(dict(status='EXACT_RELEASE_VALIDATED_NO_NATIVE_START')))
        return 0
    from src.candidate_a_natural_service_20261015.bridge import execute
    return execute(args.card,args.release)


if __name__=='__main__':
    raise SystemExit(main())
