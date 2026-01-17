import marimo

__generated_with = "0.19.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from math import sqrt
    return mo, sqrt


@app.cell
def _(mo):
    mo.md(r"""
    # Reinforced Concrete Calculator

    - Version: 0.1.0
    - Author: Gus
    - Date: now
    - License: ?

    The purpose of this calculator is to... hopefully not kill anyone!!!

    ---
    """)
    return


@app.cell
def _(Ec, mo):
    xi_cu = 0.003
    Es = 200000
    n = Es / Ec
    f_sy = 500
    md_str = rf"""
    ## Constants

    Variable      | Value     | Units  | Description
    --            | --        | --     | --
    $\xi_{{cu}}$  | {xi_cu}   |
    $E_s$         | {Es}      | mPa
    $n$           | {n:.3f}   |
    $f_{{sy}}$    | {f_sy}    | mPa

    """
    mo.md(md_str)
    return Es, f_sy, n, xi_cu


@app.cell
def _():
    # this also works
    # from common import data

    # TODO should this be a linear interpolation??
    data = {
        20: 24000,
        25: 26700,
        32: 30100,
        40: 32800,
        50: 34800,
        65: 37400,
        80: 39600,
        100: 42200,
    }
    return (data,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Simple Inputs
    """)
    return


@app.cell
def _(mo):
    # TODO nothing uses these??
    slab_beam = mo.ui.dropdown(options=["slab", "beam"], value="beam", label="slab_beam")
    slab_type = mo.ui.dropdown(options=["columns", "walls"], value="columns", label="slab_type")
    mo.vstack([slab_beam, slab_type])
    return (slab_beam,)


@app.cell
def _(slab_beam):
    slab_beam.value
    return


@app.cell
def _(mo):
    depth_ui = mo.ui.number(start=100, stop=300, step=10, value=200, label="depth")
    width_ui = mo.ui.number(start=100, stop=1200, step=100, value=1000, label="width")
    span_ui = mo.ui.number(start=1000, stop=6000, step=1000, value=5000, label="span")
    mo.vstack([depth_ui, width_ui, span_ui])
    return depth_ui, span_ui, width_ui


@app.cell
def _(depth_ui, span_ui, width_ui):
    # reassign for convenience
    depth = depth_ui.value
    width = width_ui.value
    span = span_ui.value
    return depth, width


@app.cell
def _(data, mo):
    distance_between_lateral_supports = 0
    Fc_prime = 32
    Ec = data[Fc_prime]
    as_compression = 1005
    as_tension = 1005
    g_udl = 10
    q_udl = 15
    cover_compression = 60
    cover_tension = 60
    G_servicability_factor = 1
    Q_short_servicability_factor = 0.7
    Q_long_servicability_factor = 0.4
    G_ultimate_factor = 1.2
    Q_ultimate_factor = 1.5
    mo.show_code()
    return (
        Ec,
        Fc_prime,
        as_compression,
        as_tension,
        cover_compression,
        cover_tension,
        distance_between_lateral_supports,
    )


@app.cell
def _(
    Fc_prime,
    as_compression,
    as_tension,
    cover_compression,
    cover_tension,
    depth,
    mo,
    n,
    sqrt,
):
    ## Simple outputs
    depth_to_compression_steel = cover_compression
    depth_to_tensile_steel = depth- cover_tension
    converted_compression_steel = as_compression * (n - 1)
    converted_tensile_steel = n * as_tension
    f_ct_f = 0.6 * sqrt(Fc_prime)
    Y = max(0.67, 0.97 - 0.0025 * Fc_prime)
    alpha_2 = max(0.67, 0.85 - 0.0015 * Fc_prime)

    md_str_simple = f"""
    ## Simple outputs

    {depth_to_compression_steel=} mm

    {depth_to_tensile_steel =} mm$^2$

    {converted_compression_steel=:.2f} mm$^2$

    {converted_tensile_steel=:.2f} mm
    """
    mo.md(md_str_simple)
    return (
        Y,
        alpha_2,
        converted_compression_steel,
        converted_tensile_steel,
        depth_to_compression_steel,
        depth_to_tensile_steel,
    )


@app.cell
def _(
    converted_compression_steel,
    converted_tensile_steel,
    depth_to_compression_steel,
    depth_to_tensile_steel,
    sqrt,
    width,
):
    ## Servicability dn quadratic variables
    a_s = width/ 2
    b_s = converted_compression_steel * converted_tensile_steel
    c_s = depth_to_compression_steel * converted_compression_steel + depth_to_tensile_steel * converted_tensile_steel
    c_s = (-b_s + sqrt(b_s**2 - 4 * a_s * c_s)) / (2 * a_s)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Servicability dn quadratic variables

    $$
    a_s = \frac{\textup{width}}{ 2}
    $$

    $$
    b_s = converted\_compression\_steel * converted\_tensile\_steel
    $$

    $$
    c_s = \textup{depth\_to\_compression\_steel} * \textup{converted\_compression\_steel} + \textup{depth\_to\_tensile\_steel} * \textup{converted\_tensile\_steel}
    $$

    $$
    c_s = \frac{-b_s + \sqrt{b_s^2 - 4 a_s c_s}} {2 a_s}
    $$
    """)
    return


@app.cell
def _(
    Es,
    Fc_prime,
    Y,
    alpha_2,
    as_compression,
    as_tension,
    depth_to_compression_steel,
    f_sy,
    mo,
    sqrt,
    width,
    xi_cu,
):
    a = Y * width* alpha_2 * Fc_prime  # (=Cc)
    b = Es * as_compression * xi_cu - as_tension * f_sy  # (=Cs-Ct)
    c = -xi_cu * Es * as_compression * depth_to_compression_steel  # (=Cs-Ct)
    ultimate_dn = (-b + sqrt(b**2 - 4 * a * c)) / (2 * a)
    mo.output.replace(f"ultimate_dn: {ultimate_dn:.2f}")
    return (ultimate_dn,)


@app.cell
def _(depth_to_tensile_steel, mo, ultimate_dn):
    Kuo = ultimate_dn / depth_to_tensile_steel
    if (1.24-13*Kuo/12<0.65):
        capacity_reduction_factor_bending=0.65
    elif (1.24-13*Kuo/12>0.85):
        capacity_reduction_factor_bending=0.85
    else:
        capacity_reduction_factor_bending=1.24-13*Kuo/12
    mo.output.replace(f"{capacity_reduction_factor_bending=}")
    return


@app.cell
def _(
    Es,
    Fc_prime,
    Y,
    alpha_2,
    as_compression,
    as_tension,
    depth_to_compression_steel,
    f_sy,
    ultimate_dn,
    width,
    xi_cu,
):
    # Force Equilibrium Check
    Ts = as_tension * f_sy
    Cc = width* Fc_prime * Y * alpha_2 * ultimate_dn
    eta_sc = xi_cu * (ultimate_dn - depth_to_compression_steel) / ultimate_dn
    Cs = Es * as_compression * eta_sc
    return Cc, Cs, Ts


@app.cell
def _(Cc, Cs, Ts):
    assert round(Ts - Cc - Cs) == 0, f'T/C check failed: {Ts=} (Cc + Cs)={Cc + Cs}'
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Slenderness
    """)
    return


@app.cell
def _(depth, distance_between_lateral_supports, mo, width):
    # Slenderness Limit for Continuous and Simply Supported Beams Check
    check = distance_between_lateral_supports / width < min(60, 180 * width /  depth)
    if check:
        res = 'PASS'
    else:
        res = 'FAIL'

    mo.output.replace(f"{res}")
    return


if __name__ == "__main__":
    app.run()
