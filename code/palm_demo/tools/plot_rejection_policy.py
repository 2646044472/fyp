"""Plot development risk/coverage scores without images or feature arrays."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from acceptance_policy import ROUTE_FAMILIES


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('audit',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    audit=json.loads(a.audit.read_text());profile=next(v for v in audit['profiles']if v['policy']['profiles']['fastcc']['min_margin']==.02)
    rows=[r for r in profile['known']['rows']if ROUTE_FAMILIES[r['route']]=='fastcc']
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax in axes:
        for label,color,marker,selected in[
            ('Correct, accepted','#64748b','o',[r for r in rows if r['previously_correct']and r['status']=='MATCH']),
            ('Correct, blocked','#d97706','o',[r for r in rows if r['previously_correct']and r['status']!='MATCH']),
            ('Wrong identity, blocked','#dc2626','X',[r for r in rows if not r['previously_correct']])]:
            ax.scatter([r['score']for r in selected],[r['second_score']-r['score']for r in selected],c=color,marker=marker,s=48 if marker=='X'else 28,label=label,zorder=3,alpha=.9)
        ax.axhline(.02,color='#2563eb',linestyle='--',linewidth=1.3,label='Development gap = 0.02')
        ax.axhspan(0,.02,color='#fee2e2',alpha=.45,zorder=0)
        ax.set_xlabel('Best FastCC distance (lower is better)');ax.set_ylabel('Second - best gap (higher is better)');ax.grid(alpha=.2)
    axes[0].set_title(f'All {len(rows)} ordinary FastCC decisions');axes[0].set_ylim(bottom=0)
    axes[0].legend(fontsize=8,loc='upper right')
    axes[1].set_title('Overlap among difficult decisions');axes[1].set_xlim(.30,.42);axes[1].set_ylim(-.003,.085)
    offsets={'37d0c433':(-45,24),'61f30739':(8,13),'8d6441d2':(14,-4),'08ceb3b7':(-67,-3),'4ab6388d':(28,6),'c6594831':(8,22),'fa7726ef':(-48,-12)}
    for r in rows:
        if r['sample_suffix']in offsets:
            axes[1].annotate(r['sample_suffix'],(r['score'],r['second_score']-r['score']),xytext=offsets[r['sample_suffix']],textcoords='offset points',fontsize=7,
                arrowprops=dict(arrowstyle='-',color='#94a3b8',lw=.7))
    fig.suptitle('Development rejection audit: 3 wrong blocked, 4 correct also blocked',fontsize=13)
    a.output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(a.output,dpi=160);plt.close(fig)


if __name__=='__main__':main()
