"""Los invariantes de una cartera objetivo.

Están escritos antes que el constructor de carteras (M4) a propósito: así el
criterio no se puede retocar luego para que el resultado encaje.
"""

from __future__ import annotations

import pytest

from momentum.portfolio import InvalidWeights, validate_weights
from momentum.types import Symbol

AAA = Symbol("AAA")
BBB = Symbol("BBB")


def test_una_cartera_normal_pasa() -> None:
    validate_weights({AAA: 0.6, BBB: 0.4}, max_weight=0.6)


def test_estar_en_liquidez_es_valido() -> None:
    """Sumar 0 significa no estar invertido, y es una decisión legítima."""
    validate_weights({}, max_weight=0.1)


def test_no_se_admiten_pesos_negativos() -> None:
    with pytest.raises(InvalidWeights, match="corto"):
        validate_weights({AAA: 1.2, BBB: -0.2}, max_weight=1.5)


def test_no_se_admite_pasar_del_tope_por_empresa() -> None:
    with pytest.raises(InvalidWeights, match="tope"):
        validate_weights({AAA: 0.7, BBB: 0.3}, max_weight=0.6)


def test_no_se_admite_apalancarse() -> None:
    with pytest.raises(InvalidWeights, match="suman"):
        validate_weights({AAA: 0.8, BBB: 0.8}, max_weight=0.9)


def test_no_se_admite_quedarse_a_medio_invertir_sin_querer() -> None:
    with pytest.raises(InvalidWeights, match="suman"):
        validate_weights({AAA: 0.3, BBB: 0.3}, max_weight=0.5)
