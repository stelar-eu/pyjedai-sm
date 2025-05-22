## Valentine Matching

Attributes of key: `valentine_matching`
<table>
  <tr>
    <th>Attributes</th>
    <th>Info</th>
    <th>Value Type</th>
    <th>Workflow</th>
    <th>Required</th>
  </tr>
  <tr>
	<td><code>method</code></td>
  	<td><code>Coma</code>
		<code>Cupid</code>		  
		<code>DistributionBased</code>
		<code>JaccardDistanceMatcher</code>
		<code>SimilarityFlooding</code>		  
  	</td>
  	<td><code>string</code></td>
  	<td><code>ValentineWorkflow</code></td>
	<td>&#10004;</td> 
  </tr>
<tr>
 <td><code>params</code></td>
<td>See below which parameters can be used for each method</td>
<td><code>list</code></td>
<td><code>ValentineWorkflow</code></td>
	<td></td> 
  </tr>
</table>

Attributes of key: `params`

<table>
    <tr>
        <th>Attributes</th>
        <th>Name</th>
        <th>Value Type</th>
        <th>Default Value</th>
        <th>Method</th>
    </tr>
    <tr>
        <td rowspan="10"><code>params</code></td>
        <td><code>max_n</code></td>
        <td><code>int</code></td>
        <td>0</td>
        <td rowspan="2"><code>Coma</code></td>
    </tr>
    <tr>
        <td><code>use_instances</code></td>
        <td><code>bool</code></td>
        <td>False</td>
    </tr>
    <tr>
        <td><code>w_struct</code></td>
        <td><code>float</code></td>
        <td>0.2</td>
        <td rowspan="3"><code>Cupid</code></td>
    </tr>
    <tr>
        <td><code>leaf_w_struct</code></td>
        <td><code>float</code></td>
        <td>0.2</td>
    </tr>
    <tr>
        <td><code>th_accept</code></td>
        <td><code>float</code></td>
        <td>0.7</td>
    </tr>
    <tr>
        <td><code>threshold1</code></td>
        <td><code>float</code></td>
        <td>0.15</td>
        <td rowspan="2"><code>DistributionBased</code></td>
    </tr>
    <tr>
        <td><code>threshold2</code></td>
        <td><code>float</code></td>
        <td>0.15</td>
    </tr>
    <tr>
        <td><code>threshold_leven</code></td>
        <td><code>float</code></td>
        <td>0.8</td>
        <td rowspan="1"><code>JaccardDistanceMatcher</code></td>
    </tr>
    <tr>
        <td><code>coeff_policy</code></td>
        <td><code>inverse_average</code> <code>inverse_product</code></td>
        <td><code>inverse_average</code></td>
        <td rowspan="2"><code>SimilarityFlooding</code></td>
    </tr>
    <tr>
        <td><code>formula</code></td>
        <td><code>formula_a</code> <code>formula_b</code>
        <code>formula_c</code> <code>basic</code></td>
        <td><code>formula_c</code></td>
    </tr>
</table>
