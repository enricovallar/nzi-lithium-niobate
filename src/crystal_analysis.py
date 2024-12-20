import matplotlib.pyplot as plt
import numpy as np
import meep as mp
from meep import mpb    


def calculate_effective_parameters(E_i_avg, H_j_avg, freq, k_l):
    """Calculate effective permittivity (epsilon_eff) and permeability (mu_eff).
       All quantities follow the MPB normalization convention.

    Args:
        E_i_avg (float): Averaged i-component of the electric field.
        H_j_avg (float): Averaged j-component of the magnetic field.
        freq (float): Frequency.
        k_l (float): Wave vector l-component.

    Returns:
        tuple: A tuple containing:
            - epsilon_eff (float): Effective permittivity
            - mu_eff (float): Effective permeability
    """

    epsilon_eff = (k_l / freq) * (np.real(H_j_avg) / np.real(E_i_avg))
    mu_eff = (k_l / freq) * (np.real(E_i_avg) / np.real(H_j_avg))
    
    return epsilon_eff, mu_eff





def plot_field_components(field_component1, field_component2, name1, name2, cmap="rainbow", vmin=None, vmax=None, title=""):
    """Plot two components of the converted field as subplots. It considers the real part of the field components.

    !!! example
    ```python
    plot_field_components(Ez, Hy, 'Ez', 'Hy', cmap='rainbow', vmin=-1, vmax=1)
    ```

    Args:
        cmap (str, optional): The colormap to use for the plots. Defaults to "rainbow".
        vmin (float, optional): The minimum value for the colormap. Defaults to None.
        vmax (float, optional): The maximum value for the colormap. Defaults to None.

    Returns:
        matplotlib.figure.Figure: The figure containing the plots.
    """

    # Input validation
    if not isinstance(field_component1, np.ndarray) or not isinstance(field_component2, np.ndarray):
        raise TypeError("Field components must be numpy arrays")
    if field_component1.shape != field_component2.shape:
        raise ValueError("Field components must have the same shape")

    # Create figure with specified size
    fig = plt.figure(figsize=(12, 6))
    plt.rcParams.update({'font.size': 14})  # Increase font size

    # Common plotting parameters
    plot_params = {
        'cmap': cmap,
        'origin': 'lower',
        'vmin': vmin or np.real(np.minimum(field_component1.min(), field_component2.min())),
        'vmax': vmax or np.real(np.maximum(field_component1.max(), field_component2.max())),
        'aspect': 'equal'
    }

    # Plot the first field component
    ax1 = plt.subplot(1, 2, 1)
    im1 = ax1.imshow(np.real(field_component1).T, **plot_params)
    cbar1 = plt.colorbar(im1, ax=ax1, label=f"Re({name1})")
    cbar1.ax.tick_params(labelsize=10)
    cbar1.ax.set_aspect(10)
    ax1.set_title(f'{name1}', fontsize=16)
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')

    # Plot the second field component
    ax2 = plt.subplot(1, 2, 2)
    im2 = ax2.imshow(np.real(field_component2).T, **plot_params)
    cbar2 = plt.colorbar(im2, ax=ax2, label=f"Re({name2})")
    cbar2.ax.tick_params(labelsize=10)
    cbar2.ax.set_aspect(10)
    ax2.set_title(f'{name2}', fontsize=16)
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')

    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for suptitle
    fig.suptitle(title, fontsize=18)
    return fig

def mask_field(field, mask):
    """
    Apply a mask to the field.

    !!! example

        ```python
        region_I_mask = (np.real(Hy) > 0)
        region_II_mask = (np.real(Hy) < 0)

        Ez_masked_I = mask_field(Ez, region_I_mask)
        Hy_masked_I = mask_field(Hy, region_I_mask)
        ```

    Parameters:
        field (numpy.ndarray): The field to be masked. Shape (Nx, Ny).
        mask (numpy.ndarray): The mask to apply.


    Returns:
        numpy.ndarray: The masked field.
    """
    masked_field = np.where(mask, field, 0)
    return masked_field

# Now we calculate the average fields in each region integrating. 
def integrate_field(F, resolution, periods):
    """Integrates a 2D field over a periodic domain using Simpson's rule.
    
    Args:
        F (numpy.ndarray): 2D array representing the field to be integrated.
        resolution (int): Number of points in each dimension of the grid.
        periods (int): Number of periods in the domain.
    
    Returns:
        float: The integrated value of the field normalized by the number of periods squared.
    
    !!! note

        - The domain is assumed to be square with unit size.
        - Integration is performed using a simple summation with uniform grid spacing.
        - The result is normalized by dividing by periods^2.
    """
    
    # Compute the integral of the fields using Simpson's rule
    dx = dy = 1.0 / resolution
    print("dx: ", dx, "dy: ", dy)
    F_integrated = np.sum(F)*dx*dy / periods**2

    return F_integrated


def calculate_effective_parameters(E_i_avg, H_j_avg, freq, k_l):
    """Calculate effective permittivity (epsilon_eff) and permeability (mu_eff).
       All quantities follow the MPB normalization convention.

    Args:
        E_i_avg (float): Averaged i-component of the electric field.
        H_j_avg (float): Averaged j-component of the magnetic field.
        freq (float): Frequency.
        k_l (float): Wave vector l-component.

    Returns:
        tuple: A tuple containing:

            - epsilon_eff (float): Effective permittivity
            - mu_eff (float): Effective permeability

    !!! warning
        The imaginary part of the fields is neglected in this calculation.
    """


    epsilon_eff = (k_l / freq) * (np.real(H_j_avg) / np.real(E_i_avg))
    mu_eff = (k_l / freq) * (np.real(E_i_avg) / np.real(H_j_avg))
    
    return epsilon_eff, mu_eff


def example_analysis(): 
    """
    This function is an example of how to analyze the results of a simulation. 
    It calculates the effective permittivity and permeability of the mode, and plots the field components.
    
    !!! example
        ```python
        import crystal_analysis as ca

        # These parameters are used to determine dx and dy to integrate the fields
        resolution  = mode["e_field_periodic"].shape[0]
        periods = 3
        print("Resolution: ", resolution, "Periods: ", periods, "total points: ", resolution*periods)
        ms = crystal_2d.run_dumb_simulation()
        md = mpb.MPBData(lattice=ms.get_lattice(), rectify = True, periods=periods)
        with suppress_output():
            E= md.convert(mode["e_field_periodic"], kpoint=mp.Vector3())
            H= md.convert(mode["h_field_periodic"], kpoint=mp.Vector3())
        print("Shape of E after conversion: ", E.shape)
        print("Shape of H after conversion: ", H.shape)

        Ez = np.array(E[...,2])
        Hy = np.array(H[...,1])
        print("Shape of Ez: ", Ez.shape)    
        print("Shape of Hy: ", Hy.shape)
        
        # We plot the real part of the fields in the same figure
        fig = ca.plot_field_components(Ez, Hy, '$E_z$', '$H_y$', title="Relevant components of the field")

        # The calculation of the effective parameters is done by averaging the fields over the unit cell. 
        # Since we don't want the average to be zero, we need to mask the fields and perform two integrations.

        region_I_mask = (np.real(Hy) > 0)
        region_II_mask = (np.real(Hy) < 0)

        Ez_masked_I = ca.mask_field(Ez, region_I_mask)
        Hy_masked_I = ca.mask_field(Hy, region_I_mask)
        ca.plot_field_components(Ez_masked_I, Hy_masked_I, '$E_z$', '$H_y$', vmin=-1, vmax=1, title="Region I ($H_y$ > 0)")

        Ez_masked_II = ca.mask_field(Ez, region_II_mask)
        Hy_masked_II = ca.mask_field(Hy, region_II_mask)
        ca.plot_field_components(Ez_masked_II, Hy_masked_II, '$E_z$', '$H_y$', vmin=-1, vmax=1, title="Region II ($H_y$ < 0)")

        print("Shape of Ez_masked_I: ", Ez_masked_I.shape)
        print("Shape of Hy_masked_I: ", Hy_masked_I.shape)
        # We calculate the effective parameters
        Ez_avg_I = ca.integrate_field(Ez_masked_I, resolution, periods)
        Hy_avg_I = ca.integrate_field(Hy_masked_I, resolution, periods)

        Ez_avg_II = ca.integrate_field(Ez_masked_II, resolution, periods)
        Hy_avg_II = ca.integrate_field(Hy_masked_II, resolution, periods)

        print("Ez_avg_I: ", Ez_avg_I)
        print("Hy_avg_I: ", Hy_avg_I)
        print("Ez_avg_II: ", Ez_avg_II)
        print("Hy_avg_II: ", Hy_avg_II)

        # Now we calculate the effective parameters, one value for each region
        epsilon_eff_I, mu_eff_I = ca.calculate_effective_parameters(Ez_avg_I, Hy_avg_I, mode["freq"], mode["k_point"][0])
        epsilon_eff_II, mu_eff_II = ca.calculate_effective_parameters(Ez_avg_II, Hy_avg_II, mode["freq"], mode["k_point"][0])

        print("\\nEffective parameters in region I:")
        print(" epsilon_eff: ", epsilon_eff_I)
        print(" mu_eff: ", mu_eff_I)

        print("\\nEffective parameters in region II:")
        print("epsilon_eff: ", epsilon_eff_II)
        print("mu_eff: ", mu_eff_II)
        
        # Now we calculate the effective parameters for the whole domain
        epsilon_eff = np.sqrt(epsilon_eff_I +0j)*np.sqrt(epsilon_eff_II+0j)
        mu_eff = np.sqrt(mu_eff_I +0j)*np.sqrt(mu_eff_II+0j)

        print('\\nEffective parameters for the whole domain:')
        print(' epsilon_eff: ', epsilon_eff)
        print(' mu_eff: ', mu_eff)
        ```
    """
    pass