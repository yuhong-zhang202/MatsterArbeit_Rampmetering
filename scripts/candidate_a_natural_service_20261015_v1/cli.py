"""Explicit card preparation/release entry; importing never starts SUMO."""
import argparse
import json
from src.candidate_a_natural_service_20261015 import profile


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('prepare','prepare-acceptance','validate-prepared','validate','execute','worker'))
    parser.add_argument('--card')
    parser.add_argument('--release')
    args=parser.parse_args()
    if args.action in ('prepare','prepare-acceptance'):
        card=profile.prepare(acceptance=args.action=='prepare-acceptance')
        print(json.dumps(dict(status='PREPARED_NOT_RELEASED',card=str(card),sha256=profile.sha(card))))
        return 0
    if not args.card:parser.error('card is required')
    if args.action=='validate-prepared':
        profile.validate_prepared(args.card)
        print(json.dumps(dict(status='PREPARED_NOT_RELEASED_VALIDATED_NO_NATIVE_START')))
        return 0
    if not args.release:parser.error('exact release is required')
    if args.action=='validate':
        profile.validate_release(args.card,args.release,guardian_preflight=True)
        print(json.dumps(dict(status='EXACT_RELEASE_VALIDATED_NO_NATIVE_START')))
        return 0
    if args.action=='worker':
        from src.candidate_a_natural_service_20261015.bridge import execute
        return execute(args.card,args.release)
    from src.candidate_a_natural_service_20261015.guardian import execute_guarded
    return execute_guarded(args.card,args.release)


if __name__=='__main__':
    raise SystemExit(main())
