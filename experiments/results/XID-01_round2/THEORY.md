# XID-01 Round 2 Target-Risk Decomposition

## Scope

The theorem below is a finite-hypothesis, bounded-loss learning-theory lemma. Its
uniform-convergence step is standard. The decomposition is useful here because it
separates source–target alignment from ambiguity among exact source minimizers. Only the
latter is called interaction-identification error when the competing predictors are a
visual-ignoring shortcut and a cross-modal rule.

It is not yet a computable LVLM certificate: its terms contain target risks.

## Setup

Let \(\mathcal H\) be a finite class of conditional next-token predictors. Let
\(\ell(h;z)\in[0,B]\), and define source and target risks

\[
R_S(h)=\mathbb E_{Z\sim P_S}\ell(h;Z),
\qquad
R_U(h)=\mathbb E_{Z\sim P_U}\ell(h;Z).
\]

For \(\epsilon\ge0\), let

\[
\mathcal E_\epsilon
=
\left\{
h\in\mathcal H:
R_S(h)\le \inf_{g\in\mathcal H}R_S(g)+\epsilon
\right\}.
\]

Let \(R_U^\star\) be the target risk of an ambient oracle class containing
\(\mathcal H\). Define four nonnegative terms:

\[
A_U(\mathcal H)
=
\inf_{h\in\mathcal H}R_U(h)-R_U^\star
\]

(target approximation),

\[
B_{S\to U}
=
\inf_{h\in\mathcal E_0}R_U(h)-\inf_{h\in\mathcal H}R_U(h)
\]

(best exact source minimizer's target-alignment penalty),

\[
I_{S\to U}
=
\sup_{h\in\mathcal E_0}R_U(h)-\inf_{h\in\mathcal E_0}R_U(h)
\]

(exact-source-minimizer target diameter), and

\[
G_{S\to U}(\epsilon)
=
\sup_{h\in\mathcal E_\epsilon}R_U(h)
-
\sup_{h\in\mathcal E_0}R_U(h)
\]

(finite-sample near-minimizer-set expansion). Because
\(\mathcal E_0\subseteq\mathcal E_\epsilon\), all four terms are nonnegative.

## Theorem 1: finite-class source-ERM target-risk decomposition

Let \(Z_1,\ldots,Z_n\) be IID from \(P_S\), let \(\widehat R_S\) be empirical risk, and
let

\[
\widehat h\in\arg\min_{h\in\mathcal H}\widehat R_S(h).
\]

For \(\delta\in(0,1)\), define

\[
\alpha_n(\delta)
=
B\sqrt{\frac{\log(2|\mathcal H|/\delta)}{2n}}.
\]

Then with probability at least \(1-\delta\),

\[
\boxed{
R_U(\widehat h)-R_U^\star
\le
A_U(\mathcal H)
+B_{S\to U}
+I_{S\to U}
+G_{S\to U}(2\alpha_n(\delta)).
}
\]

### Proof

For fixed \(h\), Hoeffding's inequality gives

\[
\Pr\left(
\left|\widehat R_S(h)-R_S(h)\right|>\alpha
\right)
\le
2\exp\left(-\frac{2n\alpha^2}{B^2}\right).
\]

A union bound over finite \(\mathcal H\) with
\(\alpha=\alpha_n(\delta)\) yields, with probability at least \(1-\delta\),

\[
\sup_{h\in\mathcal H}
\left|\widehat R_S(h)-R_S(h)\right|
\le
\alpha_n(\delta).
\tag{1}
\]

Let \(h_S^\star\in\arg\min_{\mathcal H}R_S\). On event (1),

\[
\begin{aligned}
R_S(\widehat h)
&\le \widehat R_S(\widehat h)+\alpha_n\\
&\le \widehat R_S(h_S^\star)+\alpha_n\\
&\le R_S(h_S^\star)+2\alpha_n.
\end{aligned}
\]

Thus

\[
\widehat h\in\mathcal E_{2\alpha_n}.
\tag{2}
\]

Using (2) and adding/subtracting the exact-set and whole-class target extrema,

\[
\begin{aligned}
R_U(\widehat h)-R_U^\star
&\le
\sup_{h\in\mathcal E_{2\alpha_n}}R_U(h)-R_U^\star\\
&=
\left[\inf_{h\in\mathcal H}R_U(h)-R_U^\star\right]\\
&\quad+
\left[\inf_{h\in\mathcal E_0}R_U(h)
-\inf_{h\in\mathcal H}R_U(h)\right]\\
&\quad+
\left[\sup_{h\in\mathcal E_0}R_U(h)
-\inf_{h\in\mathcal E_0}R_U(h)\right]\\
&\quad+
\left[\sup_{h\in\mathcal E_{2\alpha_n}}R_U(h)
-\sup_{h\in\mathcal E_0}R_U(h)\right],
\end{aligned}
\]

which is the claimed result. \(\square\)

## Corollary 1: exact interaction-identifying support

If all exact source minimizers have equal target risk, then
\(I_{S\to U}=0\). If, additionally, an exact source minimizer achieves the best target
risk in \(\mathcal H\), then \(B_{S\to U}=0\). In the population/infinite-sample limit,
where the selected rule belongs to \(\mathcal E_0\), the only remaining gap is target
approximation.

This corollary does not say that a unique parameter vector is necessary. It only requires
target-risk equivalence among exact source minimizers.

## Round1 specialization

Fix a ground-truth world \(\theta\), and let the ambient oracle be the correct
\(h_\theta\), so \(A_U=0\).

For redundant support, both \(h_0,h_1\in\mathcal E_0\), the correct member reaches the
best target risk, and the wrong member's target NLL is larger by

\[
\kappa(\eta)=\log\frac{1-\eta}{\eta}.
\]

Therefore

\[
A_U=B_{S\to U}=G_{S\to U}(0)=0,
\qquad
I_{S\to U}=\kappa(\eta).
\]

For identifying support, \(\mathcal E_0=\{h_\theta\}\), hence

\[
A_U=B_{S\to U}=I_{S\to U}=G_{S\to U}(0)=0.
\]

Round1's diagnostic cell therefore changes the exact-identification term, not
approximation, marginal coverage, or target leakage.

## Scientific interpretation

The theorem distinguishes two failure modes that a single OOD generalization gap would
mix:

- **alignment failure** \(B_{S\to U}\): even the best exact source minimizer is not
  target-optimal;
- **identification failure** \(I_{S\to U}\): exact source minimization permits both good
  and bad target rules.

In an LVLM interpretation, \(I_{S\to U}>0\) becomes specifically cross-modal only when
\(\mathcal E_0\) contains both a visual-ignoring language shortcut and a predictor using
the intended image–text interaction. The concentration argument alone is not
VLM-specific.

## Limitations and next theorem target

1. The algebra makes the bound valid, but the terms use \(R_U\) and are not directly
   observable without compromising held-out independence.
2. The finite-class Hoeffding radius cannot be inserted unchanged for neural LVLMs.
3. The theorem does not bound \(I_{S\to U}\) from a support property; that is the
   mechanism-specific missing bridge.
4. \(G_{S\to U}(2\alpha_n)\) need not vary smoothly with \(n\) without source margin or
   target continuity assumptions.
5. Optimization bias among near-minimizers is absorbed by the worst-case set expansion.

The next nontrivial step is a sufficient condition connecting a structured
interaction-diagnostic support (or a separation margin on it) to an upper bound on
\(I_{S\to U}\). Without that step, this theorem is an organizing bridge lemma rather
than a paper-level VLM generalization result.
